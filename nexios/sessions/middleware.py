from nexios.middlewares.base import BaseMiddleware
from .signed_cookies import SignedSessionManager
from .file import FileSessionManager
from nexios.http.request import Request
from nexios.http.response import NexioResponse
class SessionMiddleware(BaseMiddleware):

    async def process_request(self, request :Request, response):
        self.config = request.scope['config']
        session_cookie_name = self.config.SESSION_COOKIE_NAME or "session_id"
        managers = {
            "file":FileSessionManager,
            "cookies":SessionMiddleware
        }    
        manager_config = self.config.SESSION_MANAGER 
        manager = managers.get(manager_config,SignedSessionManager)
        session = manager(
            config=self.config,
            session_key=request.cookies.get(session_cookie_name)

        )

        await session.load()
        request.session = session

    async def process_response(self, request :Request , response :NexioResponse):
        
        if request.session.is_empty() and request.session.accessed:
            response.delete_cookie(
                key=self.config.SESSION_COOKIE_NAME or "session_id",
                
                )
            return 
        if request.session.should_set_cookie:
            await request.session.save()

            session_key = request.session.get_session_key()

            response.set_cookie(
                key = self.config.SESSION_COOKIE_NAME or "session_id",
                value=session_key,
                domain=request.session.get_cookie_domain(),
                path=request.session.get_cookie_path(),
                httponly=request.session.get_cookie_httponly(),
                secure=request.session.get_cookie_secure(),
                samesite=request.session.get_cookie_samesite(),
                expires=request.session.get_expiration_time()
                
            )

