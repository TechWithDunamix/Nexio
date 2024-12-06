# Integrating Celery with Nexios

**Celery** is a powerful task queue library that supports distributed task execution. When paired with Nexios, Celery can handle background tasks like sending emails, processing uploads, or executing long-running tasks outside the main request-response cycle.

This guide walks you through integrating **Celery** into a Nexios app.

---

### Why Use Celery with Nexios?

- **Asynchronous Background Tasks:** Offload resource-heavy operations to Celery workers.  
- **Distributed Execution:** Scale across multiple servers for high-performance workflows.  
- **Reliable Task Scheduling:** Use Celery for periodic or scheduled tasks.  
- **Resilient Queue Management:** Retry failed tasks, track task states, and monitor execution logs.

---

### Prerequisites

1. **Install Required Packages**  
   Install Celery, a message broker (e.g., Redis), and any required backend libraries:
   ```bash
   pip install celery[redis]
   pip install Nexioss
   ```

2. **Set Up a Message Broker**  
   Celery requires a message broker like Redis or RabbitMQ. For simplicity, we’ll use Redis.  

   - Install Redis and ensure it’s running:
     ```bash
     sudo apt install redis
     redis-server
     ```

---

### Configure Celery in a Nexios Project

Create a `celery_app.py` file to define and configure the Celery app:

```python
from celery import Celery

# Create a Celery instance
celery_app = Celery(
    "Nexios_app",
    broker="redis://localhost:6379/0",  # Redis as the message broker
    backend="redis://localhost:6379/0"  # Redis as the result backend
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
```

---

### Create Celery Tasks

Define tasks in a `tasks.py` file. Here’s an example of sending a welcome email asynchronously:

```python
from celery_app import celery_app

@celery_app.task
def send_welcome_email(user_email):
    """
    Simulates sending a welcome email to the user.
    """
    # Simulate a delay for the task
    import time
    time.sleep(5)
    return f"Welcome email sent to {user_email}"
```

---

###  Hook Celery into Nexios

Update your Nexios app to trigger Celery tasks.  

```python
from Nexioss import get_application
from tasks import send_welcome_email

app = get_application()

@app.post("/send-email")
async def trigger_email(request, response):
    """
    API endpoint to trigger a Celery task for sending an email.
    """
    email = data.get("email")
    if not email:
        return response.json({"error": "Email is required"}, status=400)

    # Call the Celery task
    task = send_welcome_email.delay(email)

    return response.json({"message": "Email task created", "task_id": task.id}, status=202)


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a Celery task.
    """
    from celery_app import celery_app
    task = celery_app.AsyncResult(task_id)

    return response.json({
        "task_id": task.id,
        "status": task.status,
        "result": task.result if task.ready() else "Pending",
    })
```

---

### Run the Celery Worker

Start the Celery worker to process tasks:

```bash
celery -A celery_app worker --loglevel=info
```

You should see logs indicating that the worker is ready to accept tasks.

---

###  Test the Integration

1. **Trigger a Task**  
   Make a POST request to the `/send-email` endpoint:
   ```bash
   curl -X POST http://127.0.0.1:8000/send-email -H "Content-Type: application/json" -d '{"email": "test@example.com"}'
   ```

2. **Check Task Status**  
   Use the task ID returned by the above endpoint to query the task’s status:
   ```bash
   curl http://127.0.0.1:8000/task-status/<task_id>
   ```

---

### Advanced Use Cases

1. **Periodic Tasks with Celery Beat**  
   Install `celery[redis]` and `celery-beat` to schedule periodic tasks:
   ```bash
   pip install celery-beat
   ```

   Example periodic task configuration:
   ```python
   from celery import Celery
   from celery.schedules import crontab

   celery_app.conf.beat_schedule = {
       "send-daily-summary": {
           "task": "tasks.send_summary_email",
           "schedule": crontab(hour=9, minute=0),
           "args": ("daily@example.com",),
       },
   }
   ```

2. **Task Retries**  
   Add retry logic to handle transient errors:
   ```python
   @celery_app.task(bind=True, max_retries=3)
   def unreliable_task(self):
       try:
           # Simulate a flaky operation
           risky_operation()
       except Exception as exc:
           raise self.retry(exc=exc, countdown=5)
   ```

3. **Monitoring Tasks**  
   Use tools like **Flower** to monitor and manage Celery tasks:
   ```bash
   pip install flower
   celery -A celery_app flower
   ```

---

### Why Use Celery with Nexios?

- **Decoupled Architecture:** Keep Nexios’s request-response cycle lean by offloading heavy tasks to Celery workers.  
- **Efficient Task Management:** Handle retries, scheduling, and distributed processing out of the box.  
- **Scalability:** Easily add more workers as your task queue grows.  

For further details, refer to the [Celery Documentation](https://docs.celeryproject.org).