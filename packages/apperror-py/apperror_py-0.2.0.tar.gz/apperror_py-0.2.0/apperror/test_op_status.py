import pytest

from .op_status import (
    Case,
    Code,
)


class ErrorCase(Case):
    def __init__(self, identifier: str, op_status_code: Code):
        self._identifier = identifier
        self._op_status_code = op_status_code

    def identifier(self) -> str:
        return self._identifier


def test_code_no_duplicate_value():
    code_values = set()
    for code in Code:
        if code.value in code_values:
            pytest.fail(
                f"Code value duplication found: {code.name} has value {code.value}"
            )
        code_values.add(code.value)


def test_code_str_representation():
    assert str(Code.OK) == "OK(0)"
    assert str(Code.ILLEGAL_INPUT) == "ILLEGAL_INPUT(3)"
    assert str(Code.PERMISSION_DENIED) == "PERMISSION_DENIED(7)"
    assert str(Code.TOO_MANY_REQUESTS) == "TOO_MANY_REQUESTS(8)"
    assert str(Code.UNAUTHENTICATED) == "UNAUTHENTICATED(16)"
    assert str(Code.NOT_FOUND) == "NOT_FOUND(5)"
