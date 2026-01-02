import traceback

from .app_error import AppError
from .op_status import Code, StrCase
from .test_op_status import ErrorCase


class Connection:
    def exec_sql(self, sql: str):
        raise RuntimeError("Network error")


class DBClient:
    def __init__(self, conn: Connection):
        self._conn = conn

    def insert(self, data: str):
        try:
            self._conn.exec_sql("insert into ...")
        except RuntimeError as e:
            raise AppError.new_internal_error(
                message="DB insert failed",
            ) from e


class Service:
    def __init__(self, db: DBClient):
        self._db = db

    def save(self, data: str):
        self._db.insert(data)


class API:
    def __init__(self, service: Service):
        self._service = service

    def create(self, data: str):
        self._service.save(data)


def test_app_error_print_stack():
    api = API(Service(DBClient(Connection())))
    try:
        api.create("test")
    except AppError:
        # print(f"error info: {e}")
        print(traceback.format_exc())


def test_check_app_error_cause():
    try:
        api = API(Service(DBClient(Connection())))
        api.create("test")
    except AppError as e:
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, RuntimeError)
        assert e.__cause__.args[0] == "Network error"
        assert e.__context__ is not None
        assert isinstance(e.__context__, RuntimeError)
        assert e.__context__.args[0] == "Network error"


def test_create_app_error_with_cause():
    def func_a():
        raise RuntimeError("low-level error in func_a")

    try:
        func_a()
    except RuntimeError as e:
        app_error = AppError.new_internal_error(
            message="higher-level error msg",
            cause=e,
        )
        app_error.add_err_ctx("additional err context...")
        assert app_error.__cause__ is e


def test_add_err_ctx():
    e = AppError.new_internal_error("initial error message")
    e.add_err_ctx("first context")
    e.add_err_ctx("second context")
    assert e.message == "second context -> first context -> initial error message"
    assert e.args[0] == "second context -> first context -> initial error message"


def test_custom_app_error():
    xxx_limit_exceeded = StrCase("xxx_limit_exceeded")

    class CustomAppError(AppError):
        def __init__(
            self,
            message: str,
            extra: str | None = None,
        ):
            super().__init__(
                code=Code.FAILED_PRECONDITION, case=xxx_limit_exceeded, message=message
            )
            self.extra = extra

    err = CustomAppError("custom error occurred", extra="extra info")
    assert err.extra == "extra info"
    assert f"{err}" == (
        "CustomAppError(code=FAILED_PRECONDITION(9), case=xxx_limit_exceeded, "
        "message='custom error occurred', details=None, module='none')"
    )


def test_app_error_module_property():
    e = AppError.new_internal_error(message="internal error", module="test_module")
    assert isinstance(e, AppError)
    assert e.module == "test_module"
    assert e.code == Code.INTERNAL_ERROR

    # 测试空模块名
    e = AppError.new_internal_error(message="internal error", module="")
    assert e.module == "none"

    # 测试空白字符模块名
    e = AppError.new_internal_error(message="internal error", module="   ")
    assert e.module == "none"


def test_app_error_str():
    # 测试基本错误信息
    e = AppError.new_internal_error(message="internal error")
    assert (
        str(e)
        == "AppError(code=INTERNAL_ERROR(13), case=None, message='internal error', details=None, module='none')"
    )

    # 测试带模块名的错误信息
    e = AppError.new_internal_error(message="internal error", module="test_module")
    assert (
        str(e)
        == "AppError(code=INTERNAL_ERROR(13), case=None, message='internal error', details=None, module='test_module')"
    )

    # 测试带 case 的错误信息
    e = AppError.new_internal_error(
        message="internal error", case=ErrorCase("1001", Code.INTERNAL_ERROR)
    )
    assert (
        str(e)
        == "AppError(code=INTERNAL_ERROR(13), case=1001, message='internal error', details=None, module='none')"
    )

    # 测试带 details 的错误信息
    e = AppError.new_internal_error(message="internal error", details={"key": "value"})
    assert (
        str(e)
        == "AppError(code=INTERNAL_ERROR(13), case=None, message='internal error', details={'key': 'value'}, module='none')"
    )

    # 测试完整错误信息
    e = AppError.new_internal_error(
        message="internal error",
        module="test_module",
        case=ErrorCase("1001", Code.INTERNAL_ERROR),
        details={"key": "value"},
    )
    assert (
        str(e)
        == "AppError(code=INTERNAL_ERROR(13), case=1001, message='internal error', details={'key': 'value'}, module='test_module')"
    )


def test_build_error_with_kwargs():
    # 测试不传入关键字参数
    e = AppError.new_internal_error(message="internal error")
    assert isinstance(e, AppError)
    assert e.code == Code.INTERNAL_ERROR
    assert e.message == "internal error"
    assert e.details is None

    # 测试传入关键字参数
    e = AppError.new_internal_error(
        message="internal error", details={"key1": "value1"}
    )
    assert isinstance(e, AppError)
    assert e.code == Code.INTERNAL_ERROR
    assert e.message == "internal error"
    assert e.details == {"key1": "value1"}

    # 测试传入多个关键字参数
    e = AppError.new_internal_error(
        message="internal error",
        details={"key1": "value1", "extra_info": {"key2": "value2"}},
    )
    assert isinstance(e, AppError)
    assert e.code == Code.INTERNAL_ERROR
    assert e.message == "internal error"
    assert e.details == {"key1": "value1", "extra_info": {"key2": "value2"}}


# Test AppError.new_illegal_arg method
def test_new_illegal_arg():
    # Test basic illegal argument error creation
    e = AppError.new_illegal_arg("illegal arg")
    assert e.code == Code.ILLEGAL_ARG
    assert e.message == "illegal arg"
    assert e.module == "none"

    # Test illegal argument error with custom module
    e = AppError.new_illegal_arg("illegal arg", module="validation")
    assert e.code == Code.ILLEGAL_ARG
    assert e.message == "illegal arg"
    assert e.module == "validation"

    # Test illegal argument error with empty module
    e = AppError.new_illegal_arg("illegal data", module="")
    assert e.code == Code.ILLEGAL_ARG
    assert e.message == "illegal data"
    assert e.module == "none"

    # Test illegal argument error with whitespace module
    e = AppError.new_illegal_arg("illegal format", module="   ")
    assert e.code == Code.ILLEGAL_ARG
    assert e.message == "illegal format"
    assert e.module == "none"

    # Test string representation
    e = AppError.new_illegal_arg("Test error", module="test_module")
    assert (
        str(e)
        == "AppError(code=ILLEGAL_ARG(29), case=None, message='Test error', details=None, module='test_module')"
    )


def test_add_more_err_ctx():
    def validate():
        raise AppError.new_illegal_arg("illegal arg")

    try:
        validate()
    except Exception as e:
        app_err: AppError | Exception = e
        if isinstance(e, AppError):
            e.add_err_ctx("Error while executing ...")
            app_err = e

        s = f"{app_err}"
        assert (
            s
            == "AppError(code=ILLEGAL_ARG(29), case=None, message='Error while executing ... -> illegal arg', details=None, module='none')"
        )
