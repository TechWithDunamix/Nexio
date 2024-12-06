# Routing And handlers

### What is routing ?
Routing in __*Nexios*__  works similarly to expressjs but slightly diffrent . In this case, define routes using decorators like @app.route() where the route and the HTTP methods are specified as arguments. For example, @app.route("/api/endpoint", methods=['get']) sets up a handler for GET requests at the specified endpoint.

### What is a handler  ?

A handler in nexios an async function or a class with a \__call__ Method which will be executed when the corresponding route is match it typically require only two argument (request, response)

example

```python
from nexios.cbc import APIHandler
from nexios.routers import Routes

async def function_handler(request, response):
    return response.send("Hello, this is a function type handler")

class class_handler(APIHandler):

    def get(self, request, response):
        return response.send("Hello, this a class type handler")

app.add_route(Routes(function_handler))
app.add_route(Routes(class_handler())) #Note the class based handler is instantiated

```


When a request matches this route, the corresponding asynchronous handler function (like endpoint_handler()) is called, which takes the request and response objects as arguments. Inside the function, the response is generated and sent back to the client using methods like response.send(). This allows the application to respond with the desired content, in this case, "Hello world".

Although __*Nexios*__ Provide multiple option for route handling,
Here are some examples of route paths based on strings.
This route path will match requests to the root route, /.

> Query strings are not part of the route path.


```python
@app.route("/endpoint",methods = ['get'])
async def endpoint_handler(request, response):
    return response.json({"text":"hello world"})
```
This route path will match requests to <hl1>/endpoint</hl1> and <hl1>{"text":"hello world"}</hl1> will be returned as a response . the request will only support <hl1>GET<Hl1> method


The above example is the equivalent as thise example

```python
from nexios.routers import Routes
async def endpoint_handler(request, response):
    return response.json({"text":"hello world"})

app.add_route(Routes("/endpoint",endpoint_handler,methods = ['get']))

```

<tips>
If the methods arguent is not passed the route will support all methods .
</tips>


Here are some examples of route paths based on strings.

This route path will match requests to /about.

```py
from nexios.routers import Routes

async def about_handler(request,response):
    return response.send("About Endpoint")

app.add_route(Routes("/about",about_handler))

```

This route path will match requests to /random.text.

```py
from nexios.routers import Routes

async def random_handler(request,response):
    ...

app.add_route(Routes("/random.txt",about_handler))

```

Here are some examples of route paths based on string patterns.

This route path will match acd and abcd.

```py

from nexios.routers import Routes

async def handler(request,response):
    ...

app.add_route(Routes("/ab?cd",handler))

```

This route path will match abcd, abbcd, abbbcd, and so on.

```py

async def handler(request,response):
    ...

app.add_route(Routes("/ab+cd",handler))

```
This route path will match abcd, abxcd, abRANDOMcd, ab123cd, and so on.

```
async def handler(request,response):
    ...

app.add_route(Routes("/ab*cd",handler))
```

This route path will match `/abe` and `/abcde`.

```python
from nexios.routers import Routes

async def handler(request, response):
    return response.send("Matched route: /ab(cd)?e")

app.add_route(Routes("/ab(cd)?e", handler))
```

#### **Matching Paths Ending with Specific Text**
This route path will match `butterfly` and `dragonfly`, but not `butterflyman` or `dragonflyman`.

```python
from nexios.routers import Routes

async def handler(request, response):
    return response.send("Matched route: ends with 'fly'")

app.add_route(Routes("/.*fly$", handler))
```

`Regular expression routes provide powerful matching capabilities and are ideal for dynamic or complex patterns. 
`
# Dynamic Route parameters

Dynamic Route parameters are named URL segments that are used to capture the values specified at their position in the URL. The captured values are populated in the request.route_params object, with the name of the route parameter specified in the path as their respective keys.

To define routes with route parameters, simply specify the route parameters in the path of the route as shown below.

```py

from nexios.routers import Routes

async def handler(request, response):
    print(request.route_params) #print out the value of /posts/anything
    return response.send("Route with dynamic parameter")

app.add_route(Routes("/posts/{id}", handler))

```

> Route parameter names must consist only of "word characters" ([A-Za-z0-9_]).

Since the hyphen (-) and the dot (.) are interpreted literally, they can be used along with route parameters for useful purposes.

```txt
Route path: /flights/{from}-{to}
Request URL: http://localhost:3000/flights/LAX-SFO
req.params: { "from": "LAX", "to": "SFO" }
```

```txt
Route path: /plantae/{genus}.{species}
Request URL: http://localhost:3000/plantae/Prunus.persica
req.params: { "genus": "Prunus", "species": "persica" }
```
`To have more control over the exact string that can be matched by a route parameter, you can append a regular expression in parentheses (()):`

```txt

Route path: /user/{userId}(\d+)
Request URL: http://localhost:3000/user/42
req.params: {"userId": "42"}
```
# Routers in Nexios

In Nexios, routers provide a way to better organize and manage your routes by grouping related routes together. Instead of defining routes directly in the main app, you can create routers to handle specific areas of your application, making your code more modular and easier to maintain.

A router is essentially a container for routes, which allows you to group routes based on functionality, and then you can register them with your app.
Response Methods  
The methods on the response object in the table below can send a response to the client and end the request-response cycle. If none of these methods are invoked in a route handler, the client request will remain unresolved.

# Creating a Router
To create a router in Nexios, you'll need to use the `Router` class. This allows you to specify the route paths, methods, and handlers in a more structured way.

Here is an example of how you can define and use a router in Nexios:

```python
from nexios.routers import Router
from nexios import get_application
app = get_application()
router = Router(prefix = "/api") #prefix can be skipped
app.mount_router(router)

@app.route("/create")
async def handler(request, response):
    return response.send("Hello world")
```
If a request is i made to `/api/create` the above handler reponde with `Hello world`. 


> The Router instance also contain the same routing method as the app e.g `app.add_route` ,`@app.route`,`@app.get` . e.t.c 

# Nexios Response method guide

| **Method**              | **Description**                                                                                     | **Parameters**                                                                                                                                              | **Returns**                                           | **Use Case**                                                                                                                                                         |
|-------------------------|-----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`send()`**             | Sends the response as an HTTP response.                                                              | `scope`, `receive`, `send`                                                                                                                                   | None (sends the response to the client)              | Used in asynchronous Django applications (ASGI) to send responses back to the client. It’s the core method for sending responses in async Django views.              |
| **`json()`**             | Sends a JSON response, commonly used in APIs.                                                       | `data` - Python object to be converted to JSON <br> `status_code` - HTTP status code (optional) <br> `headers` - Additional response headers (optional)      | A `JsonResponse` object (subclass of `Response`)     | Typically used for API responses where data needs to be sent in JSON format. Converts Python objects (like dictionaries) into JSON.                                  |
| **`status()`**           | Sets the HTTP status code for the response.                                                         | `status_code` - The HTTP status code to be set (e.g., 200, 404, 500)                                                                                       | The `Response` object with updated status code       | Useful when you need to modify the status code of a response based on different scenarios (e.g., error handling).                                                    |
| **`file()`**             | Sends a file as the HTTP response, supporting file streaming.                                       | `path` - Path to the file <br> `filename` - Suggested filename for download (optional) <br> `content_disposition_type` - 'inline' or 'attachment' <br> `headers` - Additional response headers (optional) | A `FileResponse` object (subclass of `Response`)     | Ideal for serving downloadable files (e.g., PDFs, images, or documents). Can be used for large file downloads as it supports streaming.                             |
| **`html()`**             | Sends an HTML response to be rendered by the browser.                                                | `content` - The HTML content to be rendered <br> `status_code` - Optional HTTP status code <br> `headers` - Additional headers for the response (optional)    | An `HTMLResponse` object (subclass of `Response`)    | Useful for returning dynamically generated HTML content from Django views. This can be rendered directly by browsers as an HTML document.                           |
| **`set_cookie()`**       | Sets a cookie in the response header.                                                                | `key` - Name of the cookie <br> `value` - Value to store in the cookie <br> `max_age` - Expiry time in seconds <br> `expires` - Expiry date <br> `path`, `domain`, `secure`, `httponly`, `samesite` - Other optional cookie attributes | None (modifies response headers)                     | Used to store cookies in the user's browser. Cookies can store session information or any user-specific data (e.g., language preference, authentication tokens).   |
| **`delete_cookie()`**    | Deletes a cookie by setting an expired date in the past.                                             | `key` - Name of the cookie to delete <br> `path`, `domain` - Optional, specify where the cookie was set                                                        | None (modifies response headers)                     | Useful for logging users out or removing stored data from the user's browser by deleting cookies.                                                                  |

