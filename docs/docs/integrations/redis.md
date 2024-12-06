# Integrating Nexios with Redis

Redis is a powerful in-memory data store used for caching, real-time data streaming, and managing ephemeral data like session storage or rate limiting. Combining Nexios with Redis can supercharge your app’s performance and scalability.

This guide explains how to integrate **Redis** with Nexios and provides examples of common use cases.

---

### Why Use Redis with Nexios?  
- **Performance:** Redis operates in-memory, making read and write operations incredibly fast.  
- **Scalability:** Great for managing real-time data in distributed systems.  
- **Versatility:** Ideal for caching, session management, pub/sub messaging, and more.  
- **Seamless Integration:** Nexios's async nature pairs well with Redis libraries like `aioredis`.

---

### Installing Redis and `aioredis`
First, ensure you have Redis installed. If you don’t have it installed, follow the [Redis installation guide](https://redis.io/docs/getting-started/).  

Install the `aioredis` library for Python:  
```bash
pip install aioredis
```

---

### Basic Setup

1. **Run Redis Server**  
   Start the Redis server on your local machine or use a cloud provider like AWS, Redis Labs, or DigitalOcean.

2. **Connect to Redis in Nexios**  
   Create a Redis connection pool when your Nexios app starts and ensure it’s properly closed when the app shuts down.  

---

### Example: Nexios + Redis Integration

Let’s create an app that uses Redis for caching user data.

#### **Step 1: Set Up Redis Connection**  
In your Nexios app, establish a connection pool with `aioredis`.

```python
from nexios import get_application
import aioredis

app = get_application()

@app.on_startup
async def startup():
    """
    Initialize Redis connection pool when the app starts.
    """
    app.redis = await aioredis.from_url("redis://localhost", decode_responses=True)

@app.on_shutdown
async def shutdown():
    """
    Close Redis connection pool when the app shuts down.
    """
    await app.redis.close()
```

---

#### **Step 2: Add Routes with Redis Operations**  
Define routes to cache and retrieve user data.

```python
@app.post("/cache")
async def cache_user(request, response):
    """
    Cache user data in Redis.
    """
    user_id = data.get("id")
    username = data.get("username")

    if not user_id or not username:
        return response.json({"error": "User ID and username are required"}, status_code=400)

    # Store user data in Redis
    await app.redis.set(f"user:{user_id}", username)
    return response.json({"message": "User cached successfully"}, status_code=201)


@app.get("/cache/{user_id}")
async def get_cached_user(request, response):
    """
    Retrieve user data from Redis.
    """
    user_id = request.route_params.user_id
    username = await app.redis.get(f"user:{user_id}")

    if not username:
        return response.json({"error": "User not found in cache"}, status_code=404)

    return response.json({"id": user_id, "username": username}, status_code=200)
```

---

#### **Step 3: Run the App**  
Start your Nexios server:  
```bash
python main.py
```

Test the API:  

- **Cache User Data**  
  ```bash
  curl -X POST http://127.0.0.1:8000/cache -H "Content-Type: application/json" -d '{"id": "1", "username": "dunamis"}'
  ```

- **Retrieve Cached User Data**  
  ```bash
  curl http://127.0.0.1:8000/cache/1
  ```

---

### Advanced Redis Use Cases

1. **Session Management:**  
   Store user session data and expiration using Redis TTL (time-to-live).  
   ```python
   await app.redis.set("session:123", "active", ex=3600)  # Expires in 1 hour
   ```

2. **Rate Limiting:**  
   Implement a simple rate limiter to control API usage.  
   ```python
   count = await app.redis.incr("rate_limit:ip:127.0.0.1")
   if count > 10:
       return response.json({"error": "Rate limit exceeded"}, status_code=429)
   ```

3. **Pub/Sub for Real-Time Apps:**  
   Use Redis Pub/Sub for real-time notifications or chat.  
   ```python
   pub = await app.redis.publish("notifications", "Hello, world!")
   ```

---

### Why Redis Enhances Nexios  
- Async capabilities of `aioredis` complement Nexios's async architecture, ensuring non-blocking performance.  
- Redis acts as a robust backend for ephemeral and real-time data needs in Nexios apps.

For more information, refer to the [Redis documentation](https://redis.io/docs/) and the [aioredis library docs](https://aioredis.readthedocs.io/).  