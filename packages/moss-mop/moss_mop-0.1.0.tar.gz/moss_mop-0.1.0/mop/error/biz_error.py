from .err_code import ErrCode

class BizError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return self.code

    @classmethod
    def init(cls, errCode: ErrCode):
        return cls(errCode.code, errCode.message)