from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from planar.ai.agent_utils import agent_configuration
from planar.ai.models import AgentConfig
from planar.evals.exceptions import EvalConflictError, EvalNotFoundError
from planar.evals.models import (
    EvalCase,
    EvalCaseResult,
    EvalRun,
    EvalRunStatus,
    EvalSet,
    EvalSuite,
)
from planar.evals.schemas import (
    AddEvalCasePayload,
    EvalCaseResultCreate,
    EvalRunCreate,
    EvalRunRead,
    EvalRunUpdate,
    EvalScorerConfig,
    EvalSetCreate,
    EvalSetUpdate,
    EvalSuiteCreate,
    EvalSuiteUpdate,
    UpdateEvalCasePayload,
)
from planar.evals.scorers import (
    scorer_registry,
)
from planar.logging import get_logger
from planar.object_config.models import (
    ConfigurableObjectType,
    ObjectConfiguration,
    ObjectConfigurationBase,
)
from planar.object_config.object_config import DEFAULT_UUID
from planar.session import get_session

logger = get_logger(__name__)


def _build_run_read(
    run: EvalRun,
    agent_config: ObjectConfigurationBase[AgentConfig] | None,
) -> EvalRunRead:
    run_data = run.model_dump()
    run_data["agent_config"] = agent_config
    return EvalRunRead.model_validate(run_data)


def _sanitize_scorer_configs_to_dict(
    scorer_configs: list[EvalScorerConfig],
) -> list[dict[str, Any]]:
    return [
        scorer_registry.sanitize_config_to_dict(scorer) for scorer in scorer_configs
    ]


async def create_eval_set(payload: EvalSetCreate) -> EvalSet:
    session = get_session()

    eval_set = EvalSet(
        name=payload.name,
        description=payload.description,
        input_format=payload.input_format,
        output_format=payload.output_format,
    )

    try:
        async with session.begin():
            session.add(eval_set)
            await session.flush()
    except IntegrityError as exc:
        logger.info("duplicate eval set name", eval_set_name=payload.name)
        raise EvalConflictError("eval set name already exists") from exc

    return eval_set


async def update_eval_set(eval_set_id: UUID, payload: EvalSetUpdate) -> EvalSet:
    session = get_session()

    async with session.begin():
        eval_set = await session.get(EvalSet, eval_set_id)
        if not eval_set:
            raise EvalNotFoundError("eval set not found")

        if payload.description is not None:
            eval_set.description = payload.description
        if payload.input_format is not None:
            eval_set.input_format = payload.input_format
        if payload.output_format is not None:
            eval_set.output_format = payload.output_format

        session.add(eval_set)
        await session.flush()

    return eval_set


async def add_eval_case(eval_set_id: UUID, payload: AddEvalCasePayload) -> EvalCase:
    """Add a new case to an eval set."""
    session = get_session()

    async with session.begin():
        eval_set = await session.get(EvalSet, eval_set_id)
        if not eval_set:
            raise EvalNotFoundError("eval set not found")

        case = EvalCase(
            eval_set_id=eval_set_id,
            input_payload=payload.input_payload,
            expected_output=payload.expected_output,
        )
        session.add(case)
        await session.flush()

    return case


async def update_eval_case(case_id: UUID, payload: UpdateEvalCasePayload) -> EvalCase:
    """Update an existing eval case."""
    session = get_session()

    async with session.begin():
        case = await session.get(EvalCase, case_id)
        if not case:
            raise EvalNotFoundError("eval set case not found")

        if payload.input_payload is not None:
            case.input_payload = payload.input_payload
        if payload.expected_output is not None:
            case.expected_output = payload.expected_output

        session.add(case)
        await session.flush()

    return case


async def delete_eval_case(case_id: UUID) -> None:
    """Delete an eval case."""
    session = get_session()

    async with session.begin():
        case = await session.get(EvalCase, case_id)
        if not case:
            raise EvalNotFoundError("eval set case not found")

        await session.delete(case)
        await session.flush()


async def list_eval_cases(eval_set_id: UUID) -> list[EvalCase]:
    session = get_session()
    statement = (
        select(EvalCase)
        .where(col(EvalCase.eval_set_id) == eval_set_id)
        .order_by(col(EvalCase.created_at))
    )
    async with session.begin_read():
        result = await session.exec(statement)
        return list(result.all())


async def list_eval_sets() -> list[EvalSet]:
    session = get_session()
    statement = select(EvalSet).order_by(col(EvalSet.name))
    async with session.begin_read():
        result = await session.exec(statement)
        return list(result.all())


async def get_eval_set(eval_set_id: UUID) -> EvalSet:
    session = get_session()
    async with session.begin_read():
        eval_set = await session.get(EvalSet, eval_set_id)
    if not eval_set:
        raise EvalNotFoundError("eval set not found")
    return eval_set


async def get_eval_set_by_name(name: str) -> EvalSet:
    session = get_session()
    statement = select(EvalSet).where(col(EvalSet.name) == name)
    async with session.begin_read():
        result = await session.exec(statement)
        eval_set = result.first()
    if not eval_set:
        raise EvalNotFoundError("eval set not found")
    return eval_set


async def create_suite(payload: EvalSuiteCreate) -> EvalSuite:
    session = get_session()

    sanitized_scorers = _sanitize_scorer_configs_to_dict(payload.scorers)

    suite = EvalSuite(
        name=payload.name,
        agent_name=payload.agent_name,
        eval_set_id=payload.eval_set_id,
        concurrency=payload.concurrency,
        scorers=sanitized_scorers,
    )

    try:
        async with session.begin():
            session.add(suite)
            await session.flush()
    except IntegrityError as exc:
        logger.info(
            "duplicate suite name for agent",
            agent_name=payload.agent_name,
            suite_name=payload.name,
        )
        raise EvalConflictError("suite name already exists for agent") from exc

    return suite


async def update_suite(suite_id: UUID, payload: EvalSuiteUpdate) -> EvalSuite:
    session = get_session()

    async with session.begin():
        suite = await session.get(EvalSuite, suite_id)
        if not suite:
            raise EvalNotFoundError("suite not found")

        if payload.eval_set_id is not None:
            suite.eval_set_id = payload.eval_set_id
        if payload.concurrency is not None:
            suite.concurrency = payload.concurrency
        if payload.scorers is not None:
            suite.scorers = _sanitize_scorer_configs_to_dict(payload.scorers)

        session.add(suite)
        await session.flush()

    return suite


async def list_suites(agent_name: str | None = None) -> list[EvalSuite]:
    session = get_session()
    statement = select(EvalSuite)
    if agent_name:
        statement = statement.where(col(EvalSuite.agent_name) == agent_name)
    statement = statement.order_by(col(EvalSuite.name))
    async with session.begin_read():
        result = await session.exec(statement)
        return list(result.all())


async def get_suite(suite_id: UUID) -> EvalSuite:
    session = get_session()
    async with session.begin_read():
        suite = await session.get(EvalSuite, suite_id)
    if not suite:
        raise EvalNotFoundError("suite not found")
    return suite


async def create_run(payload: EvalRunCreate) -> EvalRunRead:
    session = get_session()
    agent_config_id: UUID | None = payload.agent_config_id
    config_snapshot: ObjectConfigurationBase[AgentConfig] | None = None

    async with session.begin():
        suite_and_count_result = await session.exec(
            select(
                EvalSuite,
                func.count(col(EvalCase.id)).label("case_count"),
            )
            .select_from(EvalSuite)
            .outerjoin(
                EvalCase,
                col(EvalSuite.eval_set_id) == col(EvalCase.eval_set_id),
            )
            .where(col(EvalSuite.id) == payload.suite_id)
            .group_by(col(EvalSuite.id))
        )
        suite_and_count = suite_and_count_result.first()
        if not suite_and_count:
            raise EvalNotFoundError("suite not found")
        suite, total_cases = suite_and_count
        total_cases = int(total_cases or 0)
        if suite.agent_name != payload.agent_name:
            raise EvalConflictError("suite does not belong to agent")
        # check if agent config is not equal to the default config
        if agent_config_id and agent_config_id != DEFAULT_UUID:
            config_snapshot = await agent_configuration.get_config_by_id(
                agent_config_id
            )
            if not config_snapshot or config_snapshot.object_name != payload.agent_name:
                raise EvalNotFoundError("agent configuration not found")
        else:
            # Convert DEFAULT_UUID to None to avoid foreign key constraint violation.
            # DEFAULT_UUID is a sentinel value meaning "use default/active config", but
            # it doesn't exist in object_configuration table. Store NULL instead.
            agent_config_id = None

        run = EvalRun(
            agent_name=payload.agent_name,
            suite_id=payload.suite_id,
            agent_config_id=agent_config_id,
            eval_set_id=suite.eval_set_id,
            status=EvalRunStatus.PENDING,
            total_cases=total_cases,
        )

        session.add(run)
        await session.flush()

    return _build_run_read(run, config_snapshot)


async def update_run(run_id: UUID, payload: EvalRunUpdate) -> EvalRun:
    session = get_session()

    async with session.begin():
        run = await session.get(EvalRun, run_id)
        if not run:
            raise EvalNotFoundError("run not found")

        if payload.status is not None:
            run.status = payload.status
        if payload.total_cases is not None:
            run.total_cases = payload.total_cases
        if payload.error is not None:
            run.error = payload.error.model_dump(mode="json")
        if payload.started_at is not None:
            run.started_at = payload.started_at
        if payload.completed_at is not None:
            run.completed_at = payload.completed_at

        session.add(run)
        await session.flush()

    return run


async def list_runs_for_suite(suite_id: UUID) -> list[EvalRunRead]:
    session = get_session()
    statement = (
        select(EvalRun, ObjectConfiguration)
        .outerjoin(
            ObjectConfiguration,
            (col(EvalRun.agent_config_id) == col(ObjectConfiguration.id))
            & (col(ObjectConfiguration.object_type) == ConfigurableObjectType.AGENT),
        )
        .where(col(EvalRun.suite_id) == suite_id)
        .order_by(col(EvalRun.created_at).desc())
    )
    async with session.begin_read():
        result = await session.exec(statement)
        serialized: list[EvalRunRead] = []
        for run, config in result.all():
            config_snapshot: ObjectConfigurationBase[AgentConfig] | None = None
            if config:
                config_snapshot = ObjectConfigurationBase[AgentConfig].model_validate(
                    {
                        "id": config.id,
                        "object_name": config.object_name,
                        "object_type": config.object_type,
                        "created_at": config.created_at,
                        "version": config.version,
                        "data": AgentConfig.model_validate(config.data),
                        "active": config.active,
                    }
                )
            serialized.append(_build_run_read(run, config_snapshot))
        return serialized


async def get_run(run_id: UUID) -> EvalRun:
    session = get_session()
    async with session.begin_read():
        run = await session.get(EvalRun, run_id)
    if not run:
        raise EvalNotFoundError("run not found")
    return run


async def record_case_result(payload: EvalCaseResultCreate) -> EvalCaseResult:
    session = get_session()

    case_result = EvalCaseResult(
        run_id=payload.run_id,
        eval_case_id=payload.eval_case_id,
        input_payload=payload.input_payload,
        expected_output=payload.expected_output,
        agent_output=payload.agent_output,
        agent_reasoning=payload.agent_reasoning,
        tool_calls=payload.tool_calls,
        scorer_results={
            scorer_name: scorer_result.model_dump(mode="json")
            for scorer_name, scorer_result in payload.scorer_results.items()
        },
        duration_ms=payload.duration_ms,
        status=payload.status,
        error=payload.error.model_dump(mode="json") if payload.error else None,
    )

    try:
        async with session.begin():
            session.add(case_result)
            await session.flush()
    except IntegrityError as exc:
        logger.info(
            "duplicate case result for run",
            run_id=str(payload.run_id),
            eval_case_id=str(payload.eval_case_id),
        )
        raise EvalConflictError("case result already exists for run") from exc

    return case_result


async def list_case_results(run_id: UUID) -> list[EvalCaseResult]:
    session = get_session()
    statement = (
        select(EvalCaseResult)
        .where(col(EvalCaseResult.run_id) == run_id)
        .order_by(col(EvalCaseResult.eval_case_id), col(EvalCaseResult.created_at))
    )
    async with session.begin_read():
        result = await session.exec(statement)
        return list(result.all())
