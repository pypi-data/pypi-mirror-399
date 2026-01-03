class LoginError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class AuthTokenMissing(Exception):
    def __init__(self):
        super().__init__("Authentication token is missing.")
