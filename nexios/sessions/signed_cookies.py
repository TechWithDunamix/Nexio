from itsdangerous import URLSafeTimedSerializer, BadSignature
import typing
from nexios.config.settings import BaseConfig
from .base import BaseSessionInterface


class SignedSessionManager(BaseSessionInterface):
    def __init__(self, session_key: str, config: BaseConfig = BaseConfig):
        super().__init__(session_key, config)
        self.secret_key = config.secret_key
        self.serializer = URLSafeTimedSerializer(secret_key=config.SECRET_KEY,
                                                 salt="nexio.session.signed_cookie")
        session_key = session_key

    def sign_session_data(self, session_data: typing.Dict[str, typing.Any]) -> str:
        """
        Sign the session data and return a signed token (cookie value).
        """
        return self.serializer.dumps(session_data)

    def verify_session_data(self, token: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        
        """
        Verify and deserialize the signed session token.
        Returns the session data if valid, or None if invalid.
        """
        if not token:
            return  {}
        try:
            session_data = self.serializer.loads(token)
    
        
            return session_data
        except BadSignature:
            
            return {}

    def get_session_cookie(self) -> str:
        """
        Returns the session cookie that contains the signed session data.
        """
        return self.sign_session_data(self._session_cache)

    def load_session_from_cookie(self, cookie: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        cookie = self.session_key

        """
        Load the session data from a signed cookie, and verify it.
        """
        return self.verify_session_data(cookie)

    async def save(self):
        """
        Save the current session state as a signed cookie.
        """
        signed_session = self.get_session_cookie()
        self.session_key = signed_session
        return signed_session
        
    

    async def load(self):
        cookie = self.session_key
        """
        Load the session data from a signed cookie.
        """
        session_data = self.load_session_from_cookie(cookie)
        
        if session_data:
            self._session_cache.update(session_data)
        else:
            self._session_cache = {}

    def clear(self):
        self.modified = True
        self._session_cache.clear()

    
    def get_session_key(self):
        return self.session_key


