# GLPI Python SDK

Modern Python SDK for GLPI REST API with sync/async support.

> **Note:** This library was inspired by **py-glpi** and rewritten with modern Python practices, httpx support, and async capabilities.

## Features

- ✅ **Sync & Async** - Full support for synchronous and asynchronous operations
- ✅ **httpx** - Modern HTTP client with HTTP/2 support
- ✅ **FastAPI Ready** - Compatible with FastAPI and other async frameworks
- ✅ **Configurable Timeout** - Full control over connection timeouts
- ✅ **Auto Retry** - Automatic token renewal on 401/403
- ✅ **Organized Exceptions** - Exceptions by category (auth, network, resource)
- ✅ **Type Hints** - Fully typed for better DX

## Installation

```bash
pip install glpi-python-sdk
```

With HTTP/2 support:

```bash
pip install glpi-python-sdk[http2]
```

For use with FastAPI:

```bash
pip install glpi-python-sdk[fastapi]
```

## Quick Start

### Synchronous Mode

```python
from glpi_python_sdk import GLPISession

# Basic authentication
with GLPISession(
    api_url="https://glpi.example.com/apirest.php",
    app_token="your_app_token",
    auth_type="basic",
    user="admin",
    password="password",
    timeout=30.0
) as glpi:
    # Get all tickets
    tickets = glpi.get_all_items("Ticket")
    print(tickets.json())

    # Get specific item
    ticket = glpi.get_item("Ticket", 123)
    print(ticket.json())
```

### Asynchronous Mode (FastAPI)

```python
from glpi_python_sdk import AsyncGLPISession

async with AsyncGLPISession(
    api_url="https://glpi.example.com/apirest.php",
    app_token="your_app_token",
    auth_type="user_token",
    user_token="your_user_token"
) as glpi:
    tickets = await glpi.get_all_items("Ticket")
    print(tickets.json())
```

### FastAPI Example

```python
from fastapi import FastAPI, Depends
from glpi_python_sdk import AsyncGLPISession
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def get_glpi():
    async with AsyncGLPISession(
        api_url="https://glpi.example.com/apirest.php",
        app_token="token",
        auth_type="user_token",
        user_token="user_token"
    ) as session:
        yield session

@app.get("/tickets")
async def list_tickets():
    async with get_glpi() as glpi:
        response = await glpi.get_all_items("Ticket")
        return response.json()
```

## Configuration

```python
from glpi_python_sdk import GLPISession, ClientConfig

session = GLPISession(
    api_url="https://glpi.example.com/apirest.php",
    app_token="app_token",
    auth_type="basic",
    user="admin",
    password="password",
    # Connection settings
    timeout=30.0,           # Request timeout (seconds)
    connect_timeout=10.0,   # Connection timeout (seconds)
    verify_ssl=True,        # Verify SSL certificates
    max_retries=3,          # Retries on failure
    auto_refresh_token=True # Automatically refresh token
)
```

## Exceptions

```python
from glpi_python_sdk import (
    GLPIError,              # Base
    AuthenticationError,    # Authentication errors
    InvalidCredentialsError,
    SessionTokenError,
    UnauthorizedError,
    ForbiddenError,
    NetworkError,           # Network errors
    ConnectionError,
    TimeoutError,
    ResourceError,          # Resource errors
    ResourceNotFoundError,
    ItemCreationError,
)

try:
    ticket = glpi.get_item("Ticket", 99999)
except ResourceNotFoundError as e:
    print(f"Ticket not found: {e}")
except NetworkError as e:
    print(f"Connection error: {e}")
```

## Credits

This library was inspired by [py-glpi](https://github.com/teclib/py-glpi) by Teclib.

## License

MIT
