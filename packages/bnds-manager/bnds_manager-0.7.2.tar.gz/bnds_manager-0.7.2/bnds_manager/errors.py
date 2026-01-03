class ManagerVersionError(ValueError):
    pass

class AuthenticationError(ValueError):
    pass

class AuthorizationError(ValueError):
    pass

class LoginError(ValueError):
    pass

class ObjectExistsError(ValueError):
    pass