

# Nexio WebSocket Documentation
> Ensure you have installed the websockets package

```py
pip install websockets

```
## Overview
Nexio’s WebSocket module is designed for real-time, low-latency communication between clients and servers. By leveraging the WebSocket protocol, you can build features like live chats, notifications, collaborative tools, and more.

The Nexio framework provides:
- Declarative **WebSocket routes**.
- **Middleware** for advanced pre-connection logic.
- Robust **error handling** for connection and data transfer issues.
- **Stateful connections** with the ability to manage sessions and route parameters.

---

## Key Features
1. **WebSocket Route Management:** Define routes using decorators for easy organization.
2. **Connection Lifecycle Support:** Handle connection events (`accept`, `close`) seamlessly.
3. **Dynamic Parameters:** Access route-specific parameters in WebSocket connections.
4. **Custom Middleware:** Add reusable logic like authentication or logging.
5. **Error Resilience:** Gracefully handle exceptions during message processing or connection lifecycle.

---

##  Defining WebSocket Routes
The `@app.ws_route()` decorator registers WebSocket routes. A WebSocket handler is an asynchronous function that interacts with the client over a persistent connection.

### Basic Example
```python
from nexio.app import NexioApp

app = NexioApp()

@app.ws_route("/ws/echo")
async def echo_handler(ws):
    await ws.accept()
    while True:
        message = await ws.receive_text()
        await ws.send_text(f"Echo: {message}")
```

### Key Methods in WebSocket Interaction
- **`await ws.accept()`**  
  Accepts the incoming WebSocket connection.
- **`await ws.receive_text()` / `await ws.receive_bytes()`**  
  Waits to receive a text or binary message from the client.
- **`await ws.send_text(data)` / `await ws.send_bytes(data)`**  
  Sends a text or binary message back to the client.
- **`await ws.close(code=1000, reason="Reason")`**  
  Closes the WebSocket connection with a specific code and optional reason.

---

##  Middleware for WebSockets
WebSocket middleware allows you to intercept connections for tasks like authentication, logging, or rate-limiting.

### Adding Middleware
Use the `add_ws_middleware()` method to register middleware.

```python
async def auth_middleware(ws, next_middleware):
    token = ws.headers.get("Authorization")
    if not token or token != "valid_token":
        await ws.close(code=4001, reason="Unauthorized")
        return
    await next_middleware()

app.add_ws_middleware(auth_middleware)
```

- Middleware functions receive the WebSocket object and the next middleware to call.
- You can close connections directly in middleware if validation fails.

### Chaining Multiple Middlewares
Middleware functions are executed in the order they are added:

```python
async def log_middleware(ws, next_middleware):
    print(f"WebSocket request: {ws.url}")
    await next_middleware()

async def rate_limit_middleware(ws, next_middleware):
    if ws.client_ip in ["192.168.1.1"]:
        await ws.close(code=4003, reason="Rate limit exceeded")
    else:
        await next_middleware()

app.add_ws_middleware(log_middleware)
app.add_ws_middleware(rate_limit_middleware)
```

---

##  Dynamic Routing with Parameters
Dynamic parameters in routes (e.g., `/ws/user/{user_id}`) are accessible via `ws.route_params`.

```python
@app.ws_route("/ws/user/{user_id}")
async def user_handler(ws):
    user_id = ws.route_params.get("user_id")
    await ws.accept()
    await ws.send_text(f"Welcome, User {user_id}!")
```

This is useful for user-specific or room-specific WebSocket sessions.

---

##  WebSocket Lifecycle Management

### Handling Disconnections
You can handle scenarios where clients disconnect intentionally or due to network issues.

```python
@app.ws_route("/ws/lifecycle")
async def lifecycle_handler(ws):
    await ws.accept()
    try:
        while True:
            message = await ws.receive_text()
            await ws.send_text(f"Received: {message}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await ws.close(code=1000, reason="Client disconnected")
```

---

##  WebSocket Close Codes
When closing a WebSocket connection, you can specify standard WebSocket close codes:

- **1000**: Normal closure.
- **1001**: Going away (e.g., server shutting down).
- **1002**: Protocol error.
- **1003**: Unsupported data.
- **4000–4999**: Custom application-specific codes.

Example:
```python
await ws.close(code=1003, reason="Invalid data type")
```

---

##  Error Handling in WebSocket Handlers
Exceptions in WebSocket handlers are logged by default, but you can add custom logic:

```python
@app.ws_route("/ws/error")
async def error_handler(ws):
    await ws.accept()
    try:
        # Simulate an error
        raise ValueError("Something went wrong!")
    except ValueError as e:
        await ws.close(code=1011, reason=str(e))  # 1011: Internal error
    finally:
        print("WebSocket closed")
```

---

##  Advanced Usage: Broadcasting Messages
To broadcast messages to multiple clients, you can maintain a list of active WebSocket connections.

```python
active_clients = []

@app.ws_route("/ws/broadcast")
async def broadcast_handler(ws):
    await ws.accept()
    active_clients.append(ws)
    try:
        while True:
            message = await ws.receive_text()
            for client in active_clients:
                if client != ws:  # Avoid sending to the sender
                    await client.send_text(f"Broadcast: {message}")
    except Exception:
        active_clients.remove(ws)
        await ws.close()
```

---

##  Running the Nexio WebSocket Application
Nexio is ASGI-compatible, so you can run it with any ASGI server like `uvicorn` or `daphne`.

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

---

## Full Example: WebSocket Chat Application
Below is a simple group chat app using Nexio's WebSocket capabilities:

```python
from nexio.app import NexioApp

app = NexioApp()
connected_users = []

@app.ws_route("/ws/chat")
async def chat_handler(ws):
    await ws.accept()
    connected_users.append(ws)
    try:
        while True:
            message = await ws.receive_text()
            for user in connected_users:
                if user != ws:
                    await user.send_text(message)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connected_users.remove(ws)
        await ws.close(code=1000, reason="User disconnected")
```

Run with:
```bash
uvicorn app:app --reload
```

---
