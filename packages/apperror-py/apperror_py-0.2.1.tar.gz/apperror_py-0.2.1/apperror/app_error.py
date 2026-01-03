from typing import Any, Dict, Optional

from .op_status import (
    Case,
    Code,
    Request,
    Response,
    op_code_for,
)


class AppError(Exception):
    """Represents an application error."""

    _DEFAULT_MODULE = "none"

    __slots__ = ("_code", "_case", "_message", "_details", "_module")

    def __init__(
        self,
        code: Code,
        case: Case | None = None,
        message: str | None = None,
        details: Any | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ):
        msg: str
        if message:
            msg = message
        else:
            msg = code.description

        super().__init__(msg)
        self._code = code
        self._case = case
        self._message = msg
        self._details = details
        self._module = (
            module if module is not None and module.strip() else self._DEFAULT_MODULE
        )
        if cause:
            self.__cause__ = cause

    @property
    def code(self) -> Code:
        return self._code

    @property
    def case(self) -> Optional[Case]:
        return self._case

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> Any:
        return self._details

    @property
    def module(self) -> str:
        return self._module

    def add_err_ctx(self, err_ctx: str) -> None:
        """add more contextual information about current error to message."""
        if self._message:
            self._message = f"{err_ctx} -> {self._message}"
        else:
            self._message = err_ctx
        self.args = tuple(
            self._message if i == 0 else arg for i, arg in enumerate(self.args)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self._code}, case={self._case}, message='{self._message}', details={self._details}, module='{self._module}')"

    def __str__(self) -> str:
        return self.__repr__()

    # Factory functions for creating AppError instances

    @staticmethod
    def new_op_cancelled(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for cancelled operation."""
        return AppError(
            code=Code.OP_CANCELLED,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_unknown_error(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for unknown error."""
        return AppError(
            code=Code.UNKNOWN_ERROR,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_illegal_input(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for illegal input."""
        return AppError(
            code=Code.ILLEGAL_INPUT,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_timeout(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for timeout."""
        return AppError(
            code=Code.TIMEOUT,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_not_found(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for not found."""
        return AppError(
            code=Code.NOT_FOUND,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_already_exists(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for already exists."""
        return AppError(
            code=Code.ALREADY_EXISTS,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_permission_denied(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for permission denied."""
        return AppError(
            code=Code.PERMISSION_DENIED,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_unauthenticated(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for unauthenticated."""
        return AppError(
            code=Code.UNAUTHENTICATED,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_too_many_requests(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for too many requests."""
        return AppError(
            code=Code.TOO_MANY_REQUESTS,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_resource_exhausted(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Deprecated, use new_too_many_requests(...) instead."""
        return AppError.new_too_many_requests(
            message=message, case=case, details=details, module=module, cause=cause
        )

    @staticmethod
    def new_failed_precondition(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for failed precondition."""
        return AppError(
            code=Code.FAILED_PRECONDITION,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_op_conflict(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for op-conflict."""
        return AppError(
            code=Code.OP_CONFLICT,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_op_aborted(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Deprecated, use new_op_conflict(...) instead."""
        return AppError.new_op_conflict(
            message=message, case=case, details=details, module=module, cause=cause
        )

    @staticmethod
    def new_out_of_range(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for out of range."""
        return AppError(
            code=Code.OUT_OF_RANGE,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_unimplemented(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for unimplemented."""
        return AppError(
            code=Code.UNIMPLEMENTED,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_internal_error(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for internal error."""
        return AppError(
            code=Code.INTERNAL_ERROR,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_unavailable(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for unavailable."""
        return AppError(
            code=Code.UNAVAILABLE,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_illegal_state(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for illegal state."""
        return AppError(
            code=Code.ILLEGAL_STATE,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_authorization_expired(
        message: str,
        case: Optional[Case] = None,
        details: Optional[Dict[str, Any]] = None,
        module: Optional[str] = None,
        cause: Exception | None = None,
    ) -> "AppError":
        """Creates an AppError for authorization expired."""
        return AppError(
            code=Code.AUTHORIZATION_EXPIRED,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_illegal_arg(
        message: str,
        case: Case | None = None,
        details: Dict[str, Any] | None = None,
        module: str | None = None,
        cause: Exception | None = None,
    ) -> "AppError":
        return AppError(
            code=Code.ILLEGAL_ARG,
            case=case,
            message=message,
            details=details,
            module=module,
            cause=cause,
        )

    @staticmethod
    def new_from_http_resp(
        status_code: int,
        message: str | None = None,
        resp: Response | None = None,
        req: Request | None = None,
    ) -> "AppError":
        """Creates an AppError from an HTTP response."""
        op_code = op_code_for(status_code)
        details: dict[str, Any] | None = None
        if req is not None or resp is not None:
            details = {}
            if req is not None:
                details["req"] = req
            if resp is not None:
                details["resp"] = resp
        return AppError(
            code=op_code,
            message=message,
            details=details,
        )
