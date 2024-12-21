from model.error import AppError, ErrorKind


def test_app_error_initialization():
    err = AppError(ErrorKind.INTERNAL, message="Internal Server Error")

    assert err.kind == ErrorKind.INTERNAL
    assert err.message == "Internal Server Error"


def test_app_error_dict():
    err = AppError(ErrorKind.INTERNAL, message="Internal Server Error")
    result = err.dict()
    assert result == {"message": "Internal Server Error", "code": 500}
