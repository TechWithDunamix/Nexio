### Sessions in Nexios

Nexios provides a flexible and secure session management system, leveraging signed cookies and file-based session storage to maintain user state across requests. This documentation explains how sessions work in Nexios, the security mechanisms like signed cookies, and how file-based storage is configured and used.

---

## **What is a Session?**

A session in Nexios is a mechanism to persist user-specific data across multiple HTTP requests. Each user is assigned a unique session ID, which is stored securely using cookies. The server uses this ID to retrieve session data from storage during subsequent requests.

---

## **Features of Nexios Sessions**

1. **Signed Cookies for Security**
   - Nexios uses signed cookies to store the session ID. Signed cookies ensure the integrity of the data, preventing tampering by malicious users.
   - The server verifies the signature to confirm that the session data was not altered by the client.

2. **File-Based Session Storage**
   - Session data is stored on the server in a file-based storage system. This approach is lightweight and suitable for small to medium-scale applications.
   - Session files are saved in a specified directory, with the file name corresponding to the session ID.

3. **Session Expiry and Cleanup**
   - Nexios supports session expiration to automatically log users out after a period of inactivity.
   - Expired sessions are periodically cleaned up to free storage space.

---

## **How Nexios Sessions Work**

1. When a user makes a request, Nexios checks for a session cookie in the request headers.
2. If the cookie is present and valid, Nexios retrieves the corresponding session data from storage.
3. If the cookie is missing or invalid, Nexios creates a new session, generates a session ID, and sets it in a signed cookie.
4. The session data is updated in storage during the response phase, ensuring any changes are persisted.

---

## **Configuration**

### **Enabling Sessions**
To enable sessions in Nexios, you need to configure the session middleware. By default, Nexios provides a file-based session backend.

```python
from nexios import get_application,BaseConfig
from nexios.sessions import SessionMiddleware
class Appconfig(BaseConfig):
    SECRET_KEY = "very-secret-key"
   
app = get_application()


app.add_middleware(SessionMiddleware())
```

---

### **Accessing Sessions**

You can access the session object within a request handler to store or retrieve user-specific data.

```python
@app.post('/set-session')
async def set_session(request, response):
    session = request.session
    session.set_session("key","value")
    return response.send('Session set!')

@app.get('/get-session')
async def get_session(request, response):
    session = request.session
    user_id = session.get_session('user_id', 'Not logged in')  # Retrieve session data
    return response.send(f'User ID: {user_id}')
```

---

## **Signed Cookies**

Nexios ensures the integrity of session data using signed cookies. 

### **How Signed Cookies Work**
- When setting the session ID in the cookie, Nexios signs it using the `secret_key` provided in the configuration.
- The signature is a cryptographic hash that combines the session ID and the secret key.
- During subsequent requests, Nexios verifies the cookie’s signature. If the signature is invalid, the session is rejected as potentially tampered.

---

### **Example: Signed Cookie**

```python
@app.get('/set-cookie')
async def set_cookie(request, response):
    request.session.set_session("key","value")
    return response.text('Signed cookie set!')

@app.get('/read-cookie')
async def read_cookie(request, response):
    try:
        session_id = request.get_cookie('session_id', signed=True)
        return response.text(f'Session ID: {session_id}')
    except Exception as e:
        return response.text(f'Invalid or tampered cookie: {str(e)}', status=400)
```

---

## **File-Based Session Storage**

In file-based storage, Nexios saves session data in files located in a specified directory. Each session file is named after the session ID.

### **Configuration**
You can configure the storage directory and other options in the middleware.

```python
app.add_middleware(SessionMiddleware())
```

### **Session File Structure**
- **File Location**: Session files are stored in the `session_dir` directory.
- **File Content**: Each file contains serialized session data in a secure format.

---

### **Example: Using File-Based Sessions**

```python
@app.get('/set-cookie')
async def set_cookie(request, response):
    response.set_cookie('session_id', 'abcd1234', signed=True)
    return response.text('Session data stored in file!')

@app.get('/read-cookie')
async def read_cookie(request, response):
    try:
        session_id = request.get_cookie('session_id', signed=True)
        return response.text(f'Session ID: {session_id}')
    except Exception as e:
        return response.text(f'Invalid or tampered cookie: {str(e)}', status=400)
```

---

### **Session Cleanup**
Expired sessions are deleted periodically to ensure storage efficiency. This process can be configured using additional settings or a background task.



## **Advanced Features**

1. **Custom Session Backends**  
   Developers can implement custom storage backends by extending the session storage interface.

2. **Session Timeout**
   Specify a timeout to automatically expire sessions.

3. **Session Scoping**  
   Limit sessions to specific paths or domains by configuring cookie options.

---

### **Best Practices**

1. **Use Strong Secret Keys**  
   Always use a secure and random secret key for signing cookies.

2. **Secure Cookies**  
   Set the `secure` flag to ensure cookies are only transmitted over HTTPS.

3. **Implement Session Cleanup**  
   Regularly clean up expired sessions to maintain storage efficiency.

---
### **Session Cookie Configuration in Nexios**

Session cookies in Nexios are highly configurable to ensure flexibility and security. Below is an explanation of the optional parameters available for customizing session cookies, along with examples of how and why to use them.

---

#### **1. SESSION_COOKIE_NAME**  
- **Type**: `str`  
- **Description**: Specifies the name of the cookie used to store the session ID.  
- **Default**: `sessionid` (or another framework-specific default).  
- **Why Use It?**  
  If you have multiple applications on the same domain or want a custom name for the session cookie, you can set this to avoid conflicts.



#### **2. SESSION_COOKIE_DOMAIN**  
- **Type**: `str`  
- **Description**: Defines the domain for which the session cookie is valid.  
- **Default**: `None` (the cookie is valid only for the domain that set it).  
- **Why Use It?**  
  This is useful when the application needs to share the cookie across subdomains, e.g., `app.example.com` and `api.example.com`.


#### **3. SESSION_COOKIE_PATH**  
- **Type**: `str`  
- **Description**: Sets the URL path for which the cookie is valid.  
- **Default**: `/` (valid for all URLs on the domain).  
- **Why Use It?**  
  You can restrict the cookie to be sent only for specific parts of your application, e.g., `/dashboard`.



#### **4. SESSION_COOKIE_HTTPONLY**  
- **Type**: `str`  
- **Description**: Marks the cookie as HTTP-only, meaning it cannot be accessed via JavaScript (`document.cookie`).  
- **Default**: `True`.  
- **Why Use It?**  
  This enhances security by preventing client-side scripts (like malicious ones) from accessing session cookies.



#### **5. SESSION_COOKIE_SECURE**  
- **Type**: `str`  
- **Description**: Indicates that the cookie should only be transmitted over secure HTTPS connections.  
- **Default**: `False`.  
- **Why Use It?**  
  Essential for securing session data in production environments to prevent cookies from being sent over unencrypted HTTP connections.



#### **6. SESSION_COOKIE_SAMESITE**  
- **Type**: `str`  
- **Description**: Restricts the sending of cookies with cross-site requests.  
- **Options**: `"Lax"`, `"Strict"`, or `"None"`.  
  - `"Lax"`: Cookies are sent with same-site requests and top-level navigation from other sites.  
  - `"Strict"`: Cookies are sent only with same-site requests.  
  - `"None"`: Cookies are sent with all requests (requires `SESSION_COOKIE_SECURE=True`).  
- **Default**: `"Lax"`.  
- **Why Use It?**  
  Helps prevent Cross-Site Request Forgery (CSRF) attacks.

#### **7. SESSION_COOKIE_PARTITIONED**  
- **Type**: `bool`  
- **Description**: Allows cookies to be partitioned by the browser, meaning they can only be used in the context of the same top-level site.  
- **Default**: `False`.  
- **Why Use It?**  
  This improves privacy and security by preventing cookies from being shared across unrelated contexts.



### **Comprehensive Example**
Here’s a complete configuration that applies all these parameters:

```py
from nexio import get_application , BaseConfig
class AppConfig(BaseConfig):
    config_key = config_value
app = get_application(config = AppConfig())

app.add_middleware(SessionMiddleware)
```

---

### **Key Points**
1. Use **`SESSION_COOKIE_SECURE`** in production for HTTPS-only transmission.  
2. Always set **`SESSION_COOKIE_HTTPONLY`** to protect against XSS attacks.  
3. Configure **`SESSION_COOKIE_SAMESITE`** for CSRF mitigation.  
4. Use **`SESSION_COOKIE_DOMAIN`** and **`SESSION_COOKIE_PATH`** to control the scope of your session cookies.  
5. Enable **`SESSION_COOKIE_PARTITIONED`** if browser partitioning support is required.  

This flexibility allows Nexios to provide robust and secure session handling for any application.