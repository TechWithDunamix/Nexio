


# Nexios: ASGI Python Web Framework

**Nexios** is a lightweight and fast **ASGI** web framework designed for asynchronous web applications. With support for asynchronous routing, template engines, WebSockets, and real-time features, **Nexios** is optimized for high-performance, real-time, and concurrent applications.

Let's dive into the features of **Nexios** with some practical examples that showcase its power and flexibility.

## Key Features of Nexios (ASGI Framework)

### 1. **Asynchronous Routing**
In **Nexios**, routes can be defined using asynchronous functions, allowing your application to handle requests efficiently without blocking the main event loop.

#### Example:
```python
@app.route("/api/greet", methods=["GET"])
async def greet_user(req, res):
    user = await get_user_from_db(req.query["username"])
    return res.json({"message": f"Hello, {user.username}!"})
```
With **Nexios**, this simple asynchronous route can handle multiple requests concurrently, making your web application more scalable.

### 2. **Template Engine Support**
**Nexios** supports multiple template engines like **Mako**, **Jinja2**, and **Cheetah**, making it easy to render dynamic content in your web app.

#### Example:
```python
@app.route("/profile/{user_id}")
async def user_profile(req, res):
    user = await get_user_from_db(req.path_params["user_id"])
    return res.template("profile.html", {"user": user})
```
The template engine can be used asynchronously to deliver dynamic content without blocking other requests.

### 3. **Asynchronous Utilities**
For real-time web apps, handling I/O-bound tasks asynchronously is a game changer. **Nexios** provides utilities to handle file uploads, cookies, headers, and more asynchronously.

#### Example:
```python
@app.route("/upload", methods=["POST"])
async def upload_file(req, res):
    uploaded_file = await req.files.get("file")
    await save_file(uploaded_file)
    return res.json({"message": "File uploaded successfully!"})
```
The upload is processed without blocking other requests, ensuring smooth user experience even during heavy I/O operations.

### 4. **Built-In ASGI Server**
**Nexios** runs on **ASGI**-compatible servers like **Uvicorn** and **Daphne**, allowing it to handle thousands of concurrent connections efficiently.

#### Example:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
This setup ensures **Nexios** runs efficiently and scales effortlessly for applications that require high concurrency.

### 5. **Scalability and Performance**
Since **Nexios** is asynchronous by nature, it can process multiple requests simultaneously without blocking, making it ideal for real-time applications such as:

- Chat applications
- Real-time dashboards
- Online games

#### Example:
```python
@app.route("/notifications", methods=["GET"])
async def notifications(req, res):
    # Simulate long-running task (e.g., fetching notifications)
    notifications = await fetch_notifications(req.query["user_id"])
    return res.json({"notifications": notifications})
```
Even while waiting for data, **Nexios** can handle other incoming requests, making it a perfect fit for highly concurrent applications.

### 6. **WebSocket Support**
Real-time applications require bidirectional communication, and **Nexios** makes it easy to set up **WebSockets** for handling live data exchanges.

#### Example:
```python
class ChatRoom(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json({"message": "Welcome to the chat!"})

    async def on_receive(self, websocket: WebSocket, message: str) -> None:
        await websocket.send_json({"message": f"Received: {message}"})
```
**Nexios** supports WebSockets out of the box, allowing you to build chat applications or real-time data dashboards.

### 7. **Background Task Processing**
Long-running tasks can be handled in the background to ensure that the main thread remains responsive.

#### Example:
```python
@app.route("/start-task", methods=["POST"])
async def start_task(req, res):
    task_id = await start_long_running_task()
    return res.json({"message": "Task started!", "task_id": task_id})
```
With background tasks, you can start long-running operations like email processing or file uploads without slowing down the application.

### 8. **Middleware Support**
Add custom logic to the request-response cycle with **Nexios'** middleware. You can perform actions like logging, rate limiting, or user authentication before or after a request is processed.

#### Example:
```python
class AuthMiddleware(BaseMiddleware):
    async def before_request(self, req, res):
        token = req.headers.get("Authorization")
        if not token:
            return res.json({"error": "Unauthorized"}, status=401)
        user = await verify_token(token)
        req.state.user = user
        await super().before_request(req, res)
```
Middleware allows you to easily add features like authentication or logging to every route in your app.

### 9. **Session Management**
**Nexios** provides robust support for session management, allowing you to manage user sessions across multiple requests. Sessions can be stored in cookies or server-side databases.

#### Example:
```python
@app.route("/login", methods=["POST"])
async def login(req, res):
    # Authenticate user...
    await req.session.set_session("username", "dunamis")
    return res.json({"message": "Logged in successfully!"})

@app.route("/profile", methods=["GET"])
async def profile(req, res):
    username = await req.session.get_session("username")
    return res.json({"username": username})
```
Session management is built-in and can be customized based on your app’s needs.

### 10. **Tortoise ORM Support**
**Tortoise ORM** is an asynchronous ORM for **Nexios**. It supports asynchronous database queries, providing an efficient way to interact with databases in a non-blocking manner.

#### Example:
```python
class Task(Model):
    id = tortoise_fields.IntField(pk=True)
    username = tortoise_fields.CharField(max_length=120)
    dob = tortoise_fields.DatetimeField()

@app.route("/task", methods=["POST"])
async def create_task(req, res):
    task_data = await req.json()
    task = await Task.create(**task_data)
    return res.json({"task_id": task.id})
```
With **Tortoise ORM**, you can perform database operations asynchronously, improving performance when interacting with large datasets.

---

## 

With **Nexios**, you can easily build high-performance, real-time web applications that scale efficiently. The integration of **middleware**, **session management**, **Tortoise ORM**, **WebSockets**, and background task processing makes **Nexios** the perfect choice for developers looking for an ASGI-based framework to handle complex, asynchronous workflows.

From asynchronous routing and template rendering to full WebSocket support and powerful database interaction with **Tortoise ORM**, **Nexios** brings all the tools you need to build modern, scalable applications.

Ready to take your web development to the next level? **Nexios** is here to supercharge your development process and make your applications faster, more scalable, and real-time ready. Let's build the future together!

--- 

This version includes a taste of hype to show off **Nexios**'s capabilities in building scalable, performant web applications. Each feature is backed up with a real-world example to make it clear how you can integrate it into your own projects.