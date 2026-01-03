from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .http_status import HTTPStatus


class Code(Enum):
    """The set of canonical operation status codes.

    Sometimes multiple error codes may apply. Services should return the most specific error
    code that applies. For example, prefer `CodeOutOfRange` over `CodeFailedPrecondition` if both codes
    apply. Similarly prefer `CodeNotFound` or `CodeAlreadyExists` over `CodeFailedPrecondition`.
    """

    # OK not an error; returned on success.
    # HTTP Mapping: 200 OK
    OK = (0, "ok")

    # Cancelled means the operation was cancelled, typically by the caller.
    # HTTP Mapping: 499 Client Closed Request
    OP_CANCELLED = (1, "op cancelled")

    # Unknown error. For example, this error may be returned when
    # a Status value received from another address space belongs to
    # an error space that is not known in this address space. Also
    # errors raised by APIs that do not return enough error information
    # may be converted to this error.
    # HTTP Mapping: 500 Internal Server Error
    UNKNOWN_ERROR = (2, "unknown error")

    # IllegalInput means that the client specified an illegal input.
    # Note that this differs from FailedPrecondition. IllegalInput indicates
    # inputs that are problematic regardless of the state of the system
    # (e.g., a malformed file name).
    # HTTP Mapping: 400 Bad Request
    ILLEGAL_INPUT = (3, "illegal input")

    # TIMEOUT means the deadline expired before the operation could complete.
    # For operations that change the state of the system, this error may be returned
    # even if the operation has completed successfully. For example, a successful
    # response from a server could have been delayed long enough for the deadline
    # to expire.
    # HTTP Mapping: 504 Gateway Timeout
    TIMEOUT = (4, "timeout")

    # NotFound means that some requested entity (e.g., file or directory) was not found.
    # Note to server developers: if a request is denied for an entire class
    # of users, such as gradual feature rollout or undocumented allowlist,
    # NotFound may be used. If a request is denied for some users within
    # a class of users, such as user-based access control, PermissionDenied
    # must be used.
    # HTTP Mapping: 404 Not Found
    NOT_FOUND = (5, "not found")

    # AlreadyExists means that the entity that a client attempted to create
    # (e.g., file or directory) already exists.
    # HTTP Mapping: 409 Conflict
    ALREADY_EXISTS = (6, "already exists")

    # PermissionDenied means the caller does not have permission to execute the specified
    # operation. PermissionDenied must not be used for rejections caused by
    # too many requests (use TooManyRequests instead for those errors).
    # PermissionDenied must not be used if the caller can not be identified
    # (use Unauthenticated instead for those errors). This error code does not
    # imply the request is valid or the requested entity exists or satisfies
    # other pre-conditions.
    # HTTP Mapping: 403 Forbidden
    PERMISSION_DENIED = (7, "permission denied")

    # TooManyRequests means there are too many requests for some resource, perhaps
    # a per-user quota, or perhaps the entire file system is out of space.
    # HTTP Mapping: 429 Too Many Requests
    TOO_MANY_REQUESTS = (8, "too many requests")

    # FailedPrecondition means that the operation was rejected because the system
    # is not in a state required for the operation's execution. For example,
    # the directory to be deleted is non-empty, a rmdir operation is applied to
    # a non-directory, etc.
    # Service implementors can use the following guidelines to decide
    # between FailedPrecondition, OpConflict, and Unavailable:
    #  (a) Use Unavailable if the client can retry just the failing call.
    #  (b) Use OpConflict if the client should retry at a higher level. For
    #      example, when a client-specified test-and-set fails, indicating the
    #      client should restart a read-modify-write sequence.
    #  (c) Use FailedPrecondition if the client should not retry until
    #      the system state has been explicitly fixed. For example, if a "rmdir"
    #      fails because the directory is non-empty, FailedPrecondition
    #      should be returned since the client should not retry unless
    #      the files are deleted from the directory.
    # HTTP Mapping: 400 Bad Request
    FAILED_PRECONDITION = (9, "failed precondition")

    # OpConflict means there was conflicts between concurrent operation requests.
    # When this happens, the operation will be OpConflict by the server.
    # See the guidelines above for deciding between FailedPrecondition,
    # OpConflict, and Unavailable.
    # HTTP Mapping: 409 Conflict
    OP_CONFLICT = (10, "op conflict")

    # OutOfRange means that the operation was attempted past the valid range.
    # E.g., seeking or reading past end-of-file.
    # Unlike InvalidArgument, this error indicates a problem that may
    # be fixed if the system state changes. For example, a 32-bit file
    # system will generate InvalidArgument if asked to read at an
    # offset that is not in the range [0,2^32-1], but it will generate
    # OutOfRange if asked to read from an offset past the current
    # file size.
    # There is a fair bit of overlap between FailedPrecondition and
    # OutOfRange. We recommend using OutOfRange (the more specific
    # error) when it applies so that callers who are iterating through
    # a space can easily look for an OutOfRange error to detect when
    # they are done.
    # HTTP Mapping: 400 Bad Request
    OUT_OF_RANGE = (11, "out of range")

    # Unimplemented means that the operation is defined, but not implemented
    # or not supported/enabled in this service.
    # HTTP Mapping: 501 Not Implemented
    UNIMPLEMENTED = (12, "unimplemented")

    # Internal error means that some invariants expected by the underlying system
    # have been broken. This error code is reserved for serious errors.
    # HTTP Mapping: 500 Internal Server Error
    INTERNAL_ERROR = (13, "internal error")

    # Unavailable means that the service is currently unavailable. This is
    # most likely a transient condition, which can be corrected by retrying
    # with a backoff. Note that it is not always safe to retry
    # non-idempotent operations.
    # See the guidelines above for deciding between FailedPrecondition,
    # OpConflict, and Unavailable.
    # HTTP Mapping: 503 Service Unavailable
    UNAVAILABLE = (14, "unavailable")

    # IllegalState means illegal data found in datastore, unrecoverable data loss or corruption and so on.
    # HTTP Mapping: 500 Internal Server Error
    ILLEGAL_STATE = (15, "illegal state")

    # Unauthenticated means that the request does not have valid authentication
    # credentials for the operation.
    # HTTP Mapping: 401 Unauthorized
    UNAUTHENTICATED = (16, "unauthenticated")

    # The arguments passed to an operation within the program is illegal.
    # HTTP Mapping: 500 Internal Server Error
    ILLEGAL_ARG = (29, "illegal arg")

    # AuthorizationExpired means a user's authorization expired, and it is
    # needed to log-in again and reauthorize.
    # HTTP Mapping: 401 Unauthorized
    AUTHORIZATION_EXPIRED = (30, "authorization expired")

    __slots__ = ("_value", "_description")

    def __init__(self, value: int, description: str):
        self._value = value
        self._description = description

    @property
    def value(self) -> int:
        return self._value

    @property
    def description(self) -> str:
        return self._description

    def __str__(self) -> str:
        return f"{self.name}({self.value})"


_code_to_http_status = {
    Code.OK: HTTPStatus.OK,
    Code.ILLEGAL_INPUT: HTTPStatus.BAD_REQUEST,
    Code.FAILED_PRECONDITION: HTTPStatus.BAD_REQUEST,
    Code.OUT_OF_RANGE: HTTPStatus.BAD_REQUEST,
    Code.UNAUTHENTICATED: HTTPStatus.UNAUTHORIZED,
    Code.PERMISSION_DENIED: HTTPStatus.FORBIDDEN,
    Code.NOT_FOUND: HTTPStatus.NOT_FOUND,
    Code.OP_CONFLICT: HTTPStatus.CONFLICT,
    Code.ALREADY_EXISTS: HTTPStatus.CONFLICT,
    Code.TOO_MANY_REQUESTS: HTTPStatus.TOO_MANY_REQUESTS,
    Code.OP_CANCELLED: HTTPStatus.CLIENT_CLOSED_REQUEST,
    Code.ILLEGAL_STATE: HTTPStatus.INTERNAL_SERVER_ERROR,
    Code.UNKNOWN_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    Code.INTERNAL_ERROR: HTTPStatus.INTERNAL_SERVER_ERROR,
    Code.UNIMPLEMENTED: HTTPStatus.NOT_IMPLEMENTED,
    Code.UNAVAILABLE: HTTPStatus.SERVICE_UNAVAILABLE,
    Code.TIMEOUT: HTTPStatus.TIMEOUT,
    Code.AUTHORIZATION_EXPIRED: HTTPStatus.UNAUTHORIZED,
    Code.ILLEGAL_ARG: HTTPStatus.INTERNAL_SERVER_ERROR,
}


def http_status_for(code: Code) -> Optional[HTTPStatus]:
    """returns the HTTPStatus which the given OpStatusCode is mapped to."""
    return _code_to_http_status[code]


# Mapping from HTTP status to operation status code
_http_status_to_op_code: Dict[int, Code] = {
    HTTPStatus.OK: Code.OK,
    HTTPStatus.BAD_REQUEST: Code.ILLEGAL_INPUT,
    HTTPStatus.UNAUTHORIZED: Code.UNAUTHENTICATED,
    HTTPStatus.FORBIDDEN: Code.PERMISSION_DENIED,
    HTTPStatus.NOT_FOUND: Code.NOT_FOUND,
    HTTPStatus.CONFLICT: Code.ALREADY_EXISTS,
    HTTPStatus.TOO_MANY_REQUESTS: Code.TOO_MANY_REQUESTS,
    HTTPStatus.CLIENT_CLOSED_REQUEST: Code.OP_CANCELLED,
    HTTPStatus.INTERNAL_SERVER_ERROR: Code.INTERNAL_ERROR,
    HTTPStatus.NOT_IMPLEMENTED: Code.UNIMPLEMENTED,
    HTTPStatus.SERVICE_UNAVAILABLE: Code.UNAVAILABLE,
    HTTPStatus.TIMEOUT: Code.TIMEOUT,
}


def op_code_for(http_status: int) -> Code:
    """returns the op status code which the given http status is mapped to."""
    return _http_status_to_op_code.get(http_status, Code.UNKNOWN_ERROR)


class Case(ABC):
    """represents a specific error condition.
    For example: purchase_limit_exceeded, insufficient_inventory.
    """

    def __init__(self):
        pass

    @abstractmethod
    def identifier(self) -> str:
        """returns a string that uniquely identifies this error case.
        It can be a numerical value or a descriptive title/name.
        For example, two numerical values: 1000, 1_1_1000;
        a descriptive title/name: purchase_limit_exceeded.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.identifier()}"


class StrCase(Case):
    """a specific error condition identified by some words or a phrase.
    For example: purchase_limit_exceeded, insufficient_inventory.
    """

    def __init__(self, identifier: str):
        self._identifier = identifier

    def identifier(self) -> str:
        return self._identifier


@dataclass
class Request:
    url: str
    method: str
    headers: Any
    body: Any


@dataclass
class Response:
    status_code: int
    headers: Any
    body: Any
