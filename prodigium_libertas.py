import uuid
from typing import Optional

class AuthInfo:
    def __init__(self, level="PUBLIC", is_authenticated=False):
        self.level = level
        self.is_authenticated = is_authenticated
        self.can_reason_deep = level in ("VERIFIED", "ADMIN")
        self.can_access_nexus = level in ("VERIFIED", "ADMIN")
        self.can_execute_tools = level == "ADMIN"

class LibertAS:
    def __init__(self):
        self.sessions = {}

    def authorize(self, certificate: str = None, api_key: str = None) -> AuthInfo:
        if api_key == "admin-key" or certificate == "admin-cert":
            return AuthInfo(level="ADMIN", is_authenticated=True)
        if api_key or certificate:
            return AuthInfo(level="VERIFIED", is_authenticated=True)
        return AuthInfo()

    def verify_session_token(self, token: str) -> Optional[AuthInfo]:
        return self.sessions.get(token)

    def create_session_token(self, auth_info: AuthInfo) -> str:
        token = str(uuid.uuid4())
        self.sessions[token] = auth_info
        return token
