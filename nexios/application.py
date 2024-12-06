from typing import Any, Callable, List, Union
from .http.request import Request
from .http.response import NexioResponse
from .http.response import JSONResponse
from .types import HTTPMethod
from .decorators import AllowedMethods
from .routers import Router, Routes
from enum import Enum
from .config.settings import BaseConfig
import logging,traceback
from .structs import RouteParam
from .websockets import get_websocket_session
allowed_methods_default = ['get','post','delete','put','patch','options']
class NexioApp:
    def __init__(self, 
                 config: Enum = BaseConfig,
                 middlewares: list = None):
        self.config = config
        self.routes: List[Routes] = []
        self.http_middlewares: List = middlewares or []
        self.ws_middlewares: List =  []

        self.startup_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []
        self.logger = logging.getLogger("nexio")

    def on_startup(self, handler: Callable) -> Callable:
        """Decorator to register startup handlers"""
        self.startup_handlers.append(handler)
        return handler

    def on_shutdown(self, handler: Callable) -> Callable:
        """Decorator to register shutdown handlers"""
        self.shutdown_handlers.append(handler)
        return handler

    async def startup(self) -> None:
        """Execute all startup handlers sequentially"""
        for handler in self.startup_handlers:
            await handler()

    async def shutdown(self) -> None:
        """Execute all shutdown handlers sequentially with error handling"""
        for handler in self.shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                self.logger.error(f"Shutdown handler error: {str(e)}")

    async def handle_lifespan(self, receive: Callable, send: Callable) -> None:
        """Handle ASGI lifespan protocol events"""
        try:
            while True:
                message = await receive()
                
                if message["type"] == "lifespan.startup":
                    try:
                        await self.startup()
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as e:
                        self.logger.error(f"Startup error: {str(e)}")
                        await send({"type": "lifespan.startup.failed", "message": str(e)})
                        return
                
                elif message["type"] == "lifespan.shutdown":
                    try:
                        await self.shutdown()
                        await send({"type": "lifespan.shutdown.complete"})
                        return
                    except Exception as e:
                        self.logger.error(f"Shutdown error: {str(e)}")
                        await send({"type": "lifespan.shutdown.failed", "message": str(e)})
                        return

        except Exception as e:
            self.logger.error(f"Lifespan error: {str(e)}")
            if message["type"].startswith("lifespan.startup"):
                await send({"type": "lifespan.startup.failed", "message": str(e)})
            else:
                await send({"type": "lifespan.shutdown.failed", "message": str(e)})

    async def execute_middleware_stack(self, 
                                     request: Request,
                                     response: NexioResponse, 
                                     middleware: Callable, 
                                     handler: Callable, 
                                     router_middleware, 
                                     **kwargs) -> Any:
        
        
        stack = self.http_middlewares.copy()

        if router_middleware:
            stack.extend(router_middleware)
        if callable(middleware):
            stack.append(middleware)
        index = -1 
        
        async def next_middleware():
            nonlocal index
            index += 1
            
            if index < len(stack):
                middleware = stack[index]
                return await middleware(request, response, next_middleware, **kwargs)
            else:
                return await handler(request, response, **kwargs)
            
        return await next_middleware()

    async def handle_http_request(self, scope: dict, receive: Callable, send: Callable) -> None:
        
        request = Request(scope, receive, send)
        response = NexioResponse()
        request.scope['config'] = self.config

        for route in self.routes:
            
            route.handler = AllowedMethods(route.methods)(route.handler)
            
                
            match = route.pattern.match(request.url.path)
            if match:

                kwargs = match.groupdict()
                setattr(request,"route_params",RouteParam(kwargs))

                
                try:
                    await self.execute_middleware_stack(request,
                                                      response,
                                                      route.middleware,
                                                      route.handler,
                                                      route.router_middleware)
                except Exception as e:
                    self.logger.error(f"Request handler error: {str(e)}")
                    error_response = JSONResponse(
                        {"error": str(e)},
                        status_code=500
                    )
                    await error_response(scope, receive, send)
                    return
                await response(scope, receive, send)
                return

        error_response = JSONResponse({"error": "Not found"}, status_code=404)
        await error_response(scope, receive, send)

    def route(self, path: str, methods: List[Union[str, HTTPMethod]] = allowed_methods_default) -> Callable:
        
        """Decorator to register routes with optional HTTP methods"""
        def decorator(handler: Callable) -> Callable:
            handler = AllowedMethods(methods)(handler)
            self.add_route(Routes(path, handler,methods=methods))
            return handler
        return decorator
    def ws_route(self, path: str) -> Callable:
        """Decorator to register routes with optional HTTP methods"""
        def decorator(handler: Callable) -> Callable:
            self.add_route(Routes(path, handler))
            return handler
        return decorator
    def add_route(self, route: Routes) -> None:
        """Add a route to the application"""
        
       
        self.routes.append(route)

    def get(self, path: str) -> Callable:
        """GET method decorator"""
        return self.route(path, methods=["get"])

    def post(self, path: str) -> Callable:
        """POST method decorator"""
        return self.route(path, methods=["post"])

    def put(self, path: str) -> Callable:
        """PUT method decorator"""
        return self.route(path, methods=["put"])

    def delete(self, path: str) -> Callable:
        """DELETE method decorator"""
        return self.route(path, methods=["delete"])

    def patch(self, path: str) -> Callable:
        """PATCH method decorator"""
        return self.route(path, methods=["patch"])

    def options(self, path: str) -> Callable:
        """OPTIONS method decorator"""
        return self.route(path, methods=["options"])
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to the application"""
        if callable(middleware):
            self.http_middlewares.append(middleware)

    def mount_router(self, router: Router) -> None:
        """Mount a router and all its routes to the application"""
        for route in router.get_routes():
            self.add_route(route)
    async def execute_ws_middleware_stack(
        self, ws, middleware: Callable, handler: Callable, **kwargs
    ) -> Any:
        """
        Executes WebSocket middleware stack with a handler.
        """
        stack = self.ws_middlewares.copy()
        if callable(middleware):
            stack.append(middleware)
        index = -1

        async def next_middleware():
            nonlocal index
            index += 1
            if index < len(stack):
                middleware = stack[index]
                return await middleware(ws, next_middleware, **kwargs)
            else:
                return await handler(ws, **kwargs)

        return await next_middleware()

    async def handler_websocket(self, scope, receive, send):
        ws = await get_websocket_session(scope, receive, send)

        for route in self.routes:
            match = route.pattern.match(ws.url.path)
            if match:
                kwargs = match.groupdict()
                setattr(ws, "route_params", RouteParam(kwargs))

                try:
                    await self.execute_ws_middleware_stack(
                        ws,
                        route.middleware,
                        route.handler,
                        **kwargs
                    )
                except Exception as e:
                    error = traceback.format_exc()
                    self.logger.error(f"WebSocket handler error: {error}")
                    return
                return

        await ws.close(reason="Not found")

    def add_ws_middleware(self, middleware: Callable) -> None:
        """
        Add a WebSocket middleware to the application.
        """
        if callable(middleware):
            self.ws_middlewares.append(middleware)
    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """ASGI application callable"""
        if scope["type"] == "lifespan":
            await self.handle_lifespan(receive, send)
        elif scope["type"] == "http":    
            await self.handle_http_request(scope, receive, send)

        else:
            await self.handler_websocket(scope, receive, send)