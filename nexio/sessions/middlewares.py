
from nexio.sessions.backends.db import SessionStore as DBSessionStore
from nexio.http.request import Request
from nexio.http.response import NexioResponse
from nexio.middlewares.base import BaseMiddleware
class SessionMiddleware(BaseMiddleware):
    async def process_request(self, request:Request, response):
        
        #TODO:ALLOW TO USE THE SETTING TO CHANGE SESSION KEY NAME

        
        session = DBSessionStore(session_key="hello", #CHANGE:get the sesion key from cookie
                               config=request.scope['config'])
        self.session = session
        
        request.session = session
        



    async def process_response(self, request, response :NexioResponse):
        
        if self.session.modified:
            await self.session.save() 
            response.set_cookie(
                key="session_id",
                value=self.session.session_key
            )