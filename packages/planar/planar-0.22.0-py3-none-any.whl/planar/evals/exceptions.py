class EvalError(Exception):
    """Base error for evaluation operations."""


class EvalNotFoundError(EvalError):
    """Raised when an evaluation resource cannot be found."""


class EvalConflictError(EvalError):
    """Raised when an evaluation operation conflicts with existing state."""
