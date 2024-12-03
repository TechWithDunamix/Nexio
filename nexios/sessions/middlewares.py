
#TODO : deletation of sessions


from nexios.sessions.backends.db import SessionStore as DBSessionStore
from nexios.http.request import Request
from nexios.http.response import NexioResponse
from nexios.middlewares.base import BaseMiddleware
class SessionMiddleware(BaseMiddleware):
    async def process_request(self, request:Request, response):
        
        #TODO:ALLOW TO USE THE SETTING TO CHANGE SESSION KEY NAME

        key = request.cookies.get("session_id")
        session = DBSessionStore(session_key=key, 
                               config=request.scope['config'])
        self.session = session
        
        request.session = session
        



    async def process_response(self, request, response :NexioResponse):
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = await request.session.is_empty()
        except AttributeError:
            return response
        if self.session.deleted:

            response.delete_cookie(
                
                self.session.get_cookie_name(),
                self.session.session_key,
                expires=self.session.get_expiry_date(),
                httponly=self.session.get_cookie_httponly(),
                domain=self.session.get_cookie_domain(),
                path=self.session.get_cookie_path(),
                secure=self.session.get_cookie_secure(),
                partitioned=self.session.get_cookie_partitioned(),
                samesite=self.session.get_cookie_path(),
            )
            return 
        if self.session.modified:
            await self.session.save() 
            response.set_cookie(

                self.session.get_cookie_name(),
                self.session.session_key,
                expires=self.session.get_expiry_date(),
                httponly=self.session.get_cookie_httponly(),
                domain=self.session.get_cookie_domain(),
                path=self.session.get_cookie_path(),
                secure=self.session.get_cookie_secure(),
                partitioned=self.session.get_cookie_partitioned(),
                samesite=self.session.get_cookie_path(),
            )
            return