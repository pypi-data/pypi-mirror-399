from typing import Optional, Any, TypeVar, Generic

from pydantic import BaseModel, ConfigDict

from mop.error import ErrCode, BizError

DataT = TypeVar("DataT")

class Response(BaseModel, Generic[DataT]):
    model_config = ConfigDict(from_attributes=True)

    code: str
    message: str
    data: Optional[DataT] = None

class SuccessResponse(Response[Any]):
    pass

class ErrorResponse(Response[None]):
    pass

def res_success(data: Any = None, code: str = "0", message: str = "success") -> Response:
    return Response(code=code, message=message, data=data)

def res_ok(data: Any = None, code: str = "0", message: str = "ok") -> Response:
    return res_success(data=data, code=code, message=message)

def res_err(code: str = "0", message: str = "error") -> Response:
    return Response(code=code, message=message, data=None)

def res_errcode(code: ErrCode) -> Response:
    return Response(code=code.code, message=code.message, data=None)

def res_ex(err: BizError) -> Response:
    return Response(code=err.code, message=err.message, data=None)

def res_err_json(code: str = "0", message: str = "error"):
    return res_err(code=code, message=message).model_dump()