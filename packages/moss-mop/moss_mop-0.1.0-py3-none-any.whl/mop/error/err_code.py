class ErrCode:
    def __init__(self, code: str = "0", message: str = ""):
        self.code = code
        self.message = message

UNAUTHORIZED = ErrCode("Unauthorized", "未经授权")
FORBIDDEN = ErrCode("Forbidden", "无操作权限")
AUTH_FAILED = ErrCode("AuthFailed", "鉴权失败")
DATA_NOT_FOUND = ErrCode("DataNotFound", "数据未找到")
SERVER_EXCEPTION = ErrCode("ServerException", "服务端异常")
BIND_ERROR = ErrCode("BindError", "数据绑定错误")
DATA_IS_EXIST = ErrCode("DataIsExist", "同类数据已存在")
DATA_NOT_EDITABLE = ErrCode("DataNotEditable", "数据不可编辑")
DATA_CHECK_FAILURE = ErrCode("DataCheckFailure", "数据检查失败")
DATA_IS_RELATION = ErrCode("DataIsRelation", "数据被引用")
DATA_PARSE_FAILURE = ErrCode("DataParseFailure", "数据解析失败")
DATA_ENCODE_FAILURE = ErrCode("DataEncodeFailure", "数据编码失败")
DATA_DECODE_FAILURE = ErrCode("DataDecodeFailure", "数据解码失败")
BUSINESS_ERROR = ErrCode("BusinessError", "业务逻辑错误")
INTERNAL_ERROR = ErrCode("InternalError", "服务端异常")
INVALID_PARAM = ErrCode("InvalidParameter", "无效的请求参数")
INVALID_JSON = ErrCode("InvalidJson", "无效的JSON请求串")
INVALID_TOKEN = ErrCode("InvalidToken", "无效的令牌")
OPERATION_FAILURE = ErrCode("OperationFailure", "操作失败")
REMOTE_CALL_ERROR = ErrCode("RemoteCallError", "远程调用失败")
REQUEST_METHOD_NOT_SUPPORTED = ErrCode("RequestMethodNotSupported", "请求的HTTP方法不支持")
METHOD_NOT_SUPPORTED = ErrCode("MethodNotSupported", "方法不支持")

