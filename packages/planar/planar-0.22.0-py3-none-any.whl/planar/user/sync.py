from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel
from sqlalchemy.orm.strategy_options import selectinload
from sqlmodel import col, select

from planar.db.db import PlanarSession
from planar.modeling.orm.reexports import SQLModel
from planar.session import get_session
from planar.user import models as m
from planar.utils import utc_now


async def _upsert[T: SQLModel](
    session: PlanarSession,
    id_col: str,
    db_model: type[T],
    to_upsert: list[T],
    update_columns: list[str],
):
    """Create or update existing instances of the synced model."""
    if not to_upsert:
        return

    external_ids = {getattr(obj, id_col) for obj in to_upsert}
    existing_query = await session.exec(
        select(db_model).where(col(getattr(db_model, id_col)).in_(external_ids))
    )
    existing_dict = {getattr(obj, id_col): obj for obj in existing_query.all()}

    # We don't use `session.upsert` because it fires a bulk SQL insert that bypasses
    # `session.add()` and thus the `after_insert`, which is needed for the changelog.
    for obj in to_upsert:
        # Exists -> update
        if (_id := getattr(obj, id_col)) in existing_dict:
            existing = existing_dict[_id]
            for col_name in update_columns:
                setattr(existing, col_name, getattr(obj, col_name))
        # New -> create
        else:
            session.add(obj)

    upsert_query = session.upsert(
        db_model,
        to_upsert,
        conflict_columns=["external_id"],
        update_columns=update_columns,
    )
    _ = await session.exec(upsert_query)


async def _disable[T: SQLModel](
    existing_dict: dict[str, T],
    dir_objs: Sequence[BaseModel],
    dir_key: str,
):
    """Disable instances of the synced model that are no longer present."""

    new_ids: set[str] = {getattr(i, dir_key) for i in dir_objs}
    existing_ids: set[str] = set(existing_dict.keys())

    for _id in existing_ids - new_ids:
        existing_dict[_id].disabled_at = utc_now()


async def _sync_users(session: PlanarSession, dir_users: list[m.DirectoryUser]):
    existing_query = await session.exec(select(m.IDPUser))
    existing_dict = {i.external_id: i for i in existing_query}
    await _disable(existing_dict, dir_users, "sync_id")

    to_upsert = [m.IDPUser.from_directory(i) for i in dir_users]
    update_columns = [
        "email",
        "first_name",
        "last_name",
        "external_created_at",
        "external_updated_at",
        "updated_at",
        "disabled_at",  # re-enabled a previously disabled user
    ]
    await _upsert(session, "external_id", m.IDPUser, to_upsert, update_columns)


async def _sync_groups(session: PlanarSession, dir_groups: list[m.DirectoryGroup]):
    existing_query = await session.exec(select(m.IDPGroup))
    existing_dict = {i.external_id: i for i in existing_query}
    await _disable(existing_dict, dir_groups, "sync_id")

    to_upsert = [m.IDPGroup.from_directory(i) for i in dir_groups]
    update_columns = [
        "name",
        "external_created_at",
        "external_updated_at",
        "updated_at",
        "disabled_at",  # re-enabled a previously disabled user
    ]
    await _upsert(session, "external_id", m.IDPGroup, to_upsert, update_columns)

    for dir_group in dir_groups:
        await _sync_members(session, dir_group)


async def _sync_members(session: PlanarSession, dir_group: m.DirectoryGroup):
    new_external_ids = {i.sync_id for i in dir_group.members}
    users_query = await session.exec(
        select(m.IDPUser).where(col(m.IDPUser.external_id).in_(new_external_ids))
    )
    users = list(users_query.all())

    group_q = await session.exec(
        select(m.IDPGroup)
        .where(m.IDPGroup.external_id == dir_group.sync_id)
        .options(selectinload(m.IDPGroup.users_including_disabled))  # pyright: ignore[reportArgumentType]
    )
    group = group_q.one()

    # We use explicit inserts/deletes on UserGroupMembership rather than relationship assignment
    # via `group.users_including_disabled = users` because SQLA's bulk relationship sync
    # bypasses our `after_insert` and `after_delete` event listeners.

    current_user_ids = {u.id for u in group.users_including_disabled}
    new_user_ids = {u.id for u in users}

    new_users = new_user_ids - current_user_ids
    existing_users = current_user_ids - new_user_ids

    for user_id in new_users:
        membership = m.UserGroupMembership(user_id=user_id, group_id=group.id)
        session.add(membership)

    for user_id in existing_users:
        delete_query = await session.exec(
            select(m.UserGroupMembership).where(
                m.UserGroupMembership.user_id == user_id,
                m.UserGroupMembership.group_id == group.id,
            )
        )
        membership = delete_query.one()
        await session.delete(membership)


async def sync_users_and_groups(
    users: list[m.DirectoryUser], groups: list[m.DirectoryGroup]
):
    """Sync the state of the Users/Groups with the API outputs from the CoPlane backend."""

    session = get_session()

    await _sync_users(session, users)
    await _sync_groups(session, groups)
    await session.commit()
