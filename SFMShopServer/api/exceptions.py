class SFMShopException(Exception):
    pass

class ValidationError(SFMShopException):
    pass

class BusinessLogicError(SFMShopException):
    pass