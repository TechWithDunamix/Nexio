![Nexio Logo](logo.png)


# Nexios Documentation
[![GitHub stars](https://img.shields.io/github/stars/techwithdunamix/nexios.svg?style=social)](https://github.com/techwithdunamix/nexios)
[![GitHub forks](https://img.shields.io/github/forks/techwithdunamix/nexios.svg?style=social)](https://github.com/techwithdunamix/nexios)
[![GitHub issues](https://img.shields.io/github/issues/techwithdunamix/nexios.svg)](https://github.com/techwithdunamix/nexios/issues)

### Nexios Framework Documentation

---
```py

from nexios import get_application()

app = get_application()

@app.route("/endpoint",methods = ['get'])
async def api_handler(request, response):
    return response.status(200).json({"text":"Welcome to Nexios"})
```

## What is Nexios?

**Nexios** is a Python-based backend framework designed for building high-performance, stand-alone, production-grade web applications. With an opinionated approach to the Python ecosystem and its third-party libraries, Nexios ensures a streamlined development experience, requiring minimal configuration.

You can use Nexios to create Python applications that run effortlessly using standalone commands or in a WSGI/ASGI server environment for traditional deployments.

---

## Key Goals

1. **Accelerate Development:**  
   Provide a radically faster and widely accessible getting-started experience for all Python backend development.

2. **Opinionated but Flexible:**  
   Be opinionated out of the box but adapt seamlessly as your requirements evolve beyond the defaults.

3. **Built-In Non-Functional Features:**  
   Offer a comprehensive range of non-functional capabilities common to modern web applications, such as:  
   - Middleware support  
   - Security  
   - Metrics and health checks  
   - Configuration management and externalized settings  

4. **No Code Generation or Complexity:**  
   No reliance on code generation, and zero mandatory YAML/XML configurations—keeping everything Pythonic and developer-friendly.

---


## Why Choose Nexios?

- **Super Fast:** Optimized for speed and efficiency, leveraging Python’s async capabilities.  
- **Middleware Support:** Easily extend functionality with powerful middleware integration.  
- **Minimal Configuration:** Start with sensible defaults while retaining complete control over customizations.  
- **Scalable:** Designed to support projects of any size, from MVPs to enterprise-grade systems.

Nexios is your go-to choice for building high-performing, Pythonic web applications with minimal fuss and maximum productivity.  

