### Using Middleware in Nexios  

Nexios is a lightweight web framework that focuses on routing and middleware. It doesn't offer extensive built-in functionality, so an application built with Nexios primarily consists of a sequence of middleware function calls.

Middleware functions in Nexios have access to the request object , the response object , and the next middleware function in the request-response cycle, commonly referred to as `call_next`.

Middleware functions can perform various tasks, such as:

- Execute custom code
- Modify the request and response objects
- Terminate the request-response cycle
- Invoke the next middleware function in the sequence

If a middleware function doesn't end the cycle, it must call `next()` to pass control to the next function in the chain. Otherwise, the request will remain incomplete.

Nexios supports several types of middleware, allowing developers to define behavior at different stages of the request-response cycle.

`Example Middleware` 

```py
from nexios import get_application
from nexios.utils import timezone
app = get_application()

async def request_time_middleware(request, response, call_next):
    print(f"Request recieved by {timezone.now()}")

    await call_next()

app.add_middleware(request_time_middleware)

```

A nexio application can have diffrent type of middleware

- Application-level middleware
- Router-level middleware
- Error-handling middleware
- Built-in middleware
- Third-party middleware

>You can attach application-level middleware to the app using `app.add_middleware()`

### Execution order

The order in which Middleware is executed is determined by the order in which it is registered. The process before the next of the first registered Middleware is executed first, and the process after the next is executed last. See below.

```py
from nexios import get_application
from nexios.utils import timezone

app = get_application()

async def middleware_1(request, response, call_next):
    print('middleware 1 start')
    await call_next()
    print('middleware 1 end')

async def middleware_2(request, response, call_next):
    print('middleware 2 start')
    await call_next()
    print('middleware 2 end')

async def middleware_3(request, response, call_next):
    print('middleware 3 start')
    await call_next()
    print('middleware 3 end')

# Registering middleware
app.add_middleware(middleware_1)
app.add_middleware(middleware_2)
app.add_middleware(middleware_3)

@app.get('/')
async def handler(request):
    print('handler')
    return 'Hello!'

```

`Result is the following.`

```txt
middleware 1 start
  middleware 2 start
    middleware 3 start
      handler
    middleware 3 end
  middleware 2 end
middleware 1 end
```

# Modify the Response After Next




```py

async def middleware_1(request, response, call_next):
    await call_next()
    response.set_cookie("key","value")

```

# Class Bases Middlewares
Nexios supports class-based middleware, which allows for better structure and organization. You can define methods that handle the request and response separately. Here's an example:

```py
from nexios.middlewares.base import BaseMiddleware
class CustomMiddleware(BaseMiddleware):
    async def process_request(self, request, response):
        print(f"Processing request for {request.url}")

    async def process_response(self, request, response):
        response.set_header("X-Custom-Header", "value")

```

#TODO:ADD inbuilt middleware

# Third-party Middleware

Built-in middleware does not depend on external modules, but third-party middleware can depend on third-party libraries. So with them, we may make a more complex application.