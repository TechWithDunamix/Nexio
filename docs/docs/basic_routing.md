## Basic routing

##### What is a Route?

`A route is like a map that tells your app what to do when someone visits a specific web address (like /users or /products). It listens for certain HTTP methods (like GET, POST) and then runs specific code (called handlers) to respond to the request.`




Routing is basically figuring out how your app responds when a client hits a specific endpoint, which is a URI (or path) paired with an HTTP method (like GET, POST, etc.).

Each route can have one or more functions that handle the request, and these functions run when the route gets matched.


Nexios provide many style for routing includid decorators,router etc.

Below is a basic routing with decorators :


```python

@app.route("/api/endpoint",methods = ['get'])
async def endpoint_handler(request, response):

    return response.send("Hello world")
```

Explanation

- app : This refer to the app instance seen in the [Hello world example](hello_world.md)
- .route : This is a method provided by the app instance as a [decorator](https://www.geeksforgeeks.org/decorators-in-python/)

- /api/endpoint : This is the route that is refers to the route e.g www.domain.com/endpoint

- methods : define how a client interacts with a server. Common methods include GET (retrieve), POST (create), PUT (update), DELETE (remove), and PATCH (partially update).

- Handler Function(endpoint_handler): This is the async function that gets triggered when the route is matched. It handles the incoming request and decides what to send back as a response.

For more details about routing, see [the routing guide]( core-features/routing.md).