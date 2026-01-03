from uuid import UUID

from sqlalchemy.orm.strategy_options import joinedload, selectinload
from sqlmodel import select

from planar.human.exceptions import TaskNotFound, TaskNotPending, UserNotFound
from planar.human.models import Assignment, HumanTask, HumanTaskStatus, TaskScope
from planar.logging import get_logger
from planar.security.auth_context import require_principal
from planar.security.authorization import (
    AssignmentResource,
    HumanTaskAction,
    HumanTaskResource,
    UserResource,
    validate_authorization_for,
)
from planar.session import get_session
from planar.user.models import IDPUser
from planar.utils import utc_now

logger = get_logger(__name__)


def _no_op(existing_assignment: Assignment | None, user_id: UUID | None) -> bool:
    # Task is being assigned to the current assignee -> no-op
    if out := existing_assignment and existing_assignment.assignee_id == user_id:
        return out
    # Unassigned task is being unassigned -> no-op
    if out := not existing_assignment and not user_id:
        return out
    return False


async def reassign_task(task_id: UUID, assign_to: UUID | None) -> None:
    """Reassign a PENDING human task to a different user, or unassign it."""
    logger.debug("reassigning human task", task_id=task_id, user_id=assign_to)

    session = get_session()

    task_query = await session.exec(
        select(HumanTask)
        .where(HumanTask.id == task_id)
        .options(
            joinedload(HumanTask.assignment)
            .joinedload(Assignment.assignee)
            .selectinload(IDPUser.groups)  # pyright: ignore[reportArgumentType]
        )
        .options(
            joinedload(HumanTask.assignment)
            .joinedload(Assignment.assignor)
            .selectinload(IDPUser.groups)  # pyright: ignore[reportArgumentType]
        )
        .options(
            joinedload(HumanTask.scope).selectinload(TaskScope.groups)  # pyright: ignore[reportArgumentType]
        )
        .options(
            joinedload(HumanTask.scope).selectinload(TaskScope.users)  # pyright: ignore[reportArgumentType]
        )
    )
    task = task_query.first()
    if not task:
        logger.warning("human task not found for reassignment", task_id=task_id)
        raise TaskNotFound(task_id)

    if task.status != HumanTaskStatus.PENDING:
        logger.warning(
            "attempt to reassign human task not in pending status",
            task_id=task_id,
            status=task.status,
        )
        raise TaskNotPending(task_id, task.status)

    existing_assignment = task.assignment
    if _no_op(existing_assignment, assign_to):
        return

    principal = require_principal()
    if principal.user is None:
        raise UserNotFound(principal.user_email)

    if assign_to:
        assign_to_user_result = await session.exec(
            select(IDPUser)
            .where(IDPUser.id == assign_to)
            .options(selectinload(IDPUser.groups))  # pyright: ignore[reportArgumentType]
        )
        assign_to_user = assign_to_user_result.one_or_none()
        if not assign_to_user:
            raise UserNotFound(str(assign_to))
        assignee = UserResource.from_user(assign_to_user)
    else:
        assignee = None

    proposed_assignment = AssignmentResource(
        task_id=str(task.id),
        assignee=assignee,
        assignor=principal.user,
    )

    validate_authorization_for(
        HumanTaskResource.from_human_task(task, proposed_assignment),
        HumanTaskAction.TASK_ASSIGN,
    )

    if existing_assignment:
        if existing_assignment.assignee_id == assign_to:
            raise Exception(
                "attempt to reassign task to current assignee (should be caught by _no_op)"
            )
        existing_assignment.disabled_at = utc_now()
        session.add(existing_assignment)

    if assign_to:
        new_assignment = Assignment(
            task_id=task_id,
            assignee_id=assign_to,
            assignor_id=UUID(principal.user.user_id),
        )
        session.add(new_assignment)
        logger.info("human task reassigned", user_id=assign_to, task_id=task_id)
    elif existing_assignment:
        # An unassignment is disabling the existing `Assignment` without replacing it.
        logger.info("human task unassigned", task_id=task_id)
    else:
        raise Exception(
            "attempt to unassign a unassigned task (should be caught by _no_op)"
        )

    await session.commit()
