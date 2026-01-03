# MoP

MoP is a lightweight Python backend framework built on FastAPI and SQLAlchemy, providing core functionality modules for building modern web applications.

## Features

- **Configuration Management**: Flexible configuration system with easy-to-use settings
- **Database Support**: Both synchronous and asynchronous database sessions with SQLAlchemy
- **Entity Framework**: Base entity class for consistent data modeling
- **Error Handling**: Centralized error handling with business error codes
- **Logging**: Structured logging with structlog
- **Response Formatting**: Consistent API response formatting
- **CRUD Operations**: Generic CRUD operations with pagination support
- **Utilities**: Various utility functions for dates, strings, files, and more
- **Snowflake ID Generation**: Distributed unique ID generation

## Installation

```bash
pip install moss-mop
```

Or using uv:

```bash
uv add moss-mop
```

## Requirements

- Python 3.12+
- FastAPI 0.124.4+
- SQLAlchemy 2.0.45+
- Pydantic 2.12.5+
- structlog 25.5.0+
- ascii-colors 0.11.6+

## Project Structure

```
mop/
├── conf/                # Configuration management
├── db/                  # Database connections
├── entity/              # Base entity class
├── error/               # Error handling
├── logging/             # Logging configuration
├── response/            # Response formatting
├── crud/                # CRUD operations
├── util/                # Utility functions
└── snowflake.py         # Snowflake ID generation
```

## Quick Start

### 1. Configuration

```python
from mop.conf import settings

# Access configuration settings
print(settings.APP_NAME)
print(settings.DATABASE_URL)
```

### 2. Database Setup

```python
from mop.db import session, async_session
from sqlalchemy import select
from your_model import User

# Synchronous session
with session() as db:
    users = db.execute(select(User)).scalars().all()
    print(users)

# Asynchronous session
async with async_session() as db:
    users = await db.execute(select(User))
    users = users.scalars().all()
    print(users)
```

### 3. Creating Models

```python
from mop.entity import Entity
from sqlalchemy import Column, String


class User(Entity):
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
```

### 4. Error Handling

```python
from mop.error import BusinessError, ErrCode

# Raise business error
raise BusinessError(ErrCode.USER_NOT_FOUND, "User not found")
```

### 5. Logging

```python
from mop.logging import logger

# Log messages
logger.info("User logged in", user_id=123)
logger.error("Failed to process request", error="Invalid input")
```

### 6. Response Formatting

```python
from mop.response import Response, PageResponse
from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def get_users():
    users = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
    return Response(data=users, message="Success")


@app.get("/users/page")
async def get_users_page():
    users = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
    return PageResponse(data=users, total=100, page=1, page_size=20)
```

### 7. CRUD Operations

```python
from mop.crud import CRUDBase
from your_model import User, UserCreate, UserUpdate

# Create CRUD instance
user_crud = CRUDBase(User)

# Create user
user = user_crud.create(db, obj_in=UserCreate(username="test", email="test@example.com"))

# Get user by ID
user = user_crud.get(db, id=1)

# Update user
user = user_crud.update(db, db_obj=user, obj_in=UserUpdate(email="new@example.com"))

# Delete user
user_crud.remove(db, id=1)

# Get users with pagination
users, total = user_crud.get_multi(db, page=1, page_size=10)
```

### 8. Snowflake ID Generation

```python
from mop.snowflake import SnowflakeGenerator

# Create generator instance
generator = SnowflakeGenerator(datacenter_id=1, worker_id=1)

# Generate unique ID
unique_id = generator.generate()
print(unique_id)
```

## Utilities

### Date Utilities

```python
from mop.util.dates import format_datetime, parse_datetime

# Format datetime
formatted = format_datetime(datetime.now())
print(formatted)

# Parse datetime
parsed = parse_datetime("2023-01-01 12:00:00")
print(parsed)
```

### String Utilities

```python
from mop.util.strings import random_string, is_email_valid

# Generate random string
rand_str = random_string(10)
print(rand_str)

# Check if email is valid
is_valid = is_email_valid("test@example.com")
print(is_valid)
```

### File Utilities

```python
from mop.util.files import read_file, write_file

# Read file
content = read_file("test.txt")
print(content)

# Write file
write_file("test.txt", "Hello, World!")
```

## Changelog

### Version 0.1.0 (2025-12-15)

#### Added
- Initial release of MoP framework
- Configuration management module
- Database support with synchronous and asynchronous sessions
- Base entity class for data modeling
- Centralized error handling system
- Structured logging configuration
- Consistent API response formatting
- Generic CRUD operations with pagination
- Utility functions for dates, strings, files, and more
- Snowflake ID generation for distributed systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Author

- **puras** - [puras.he@gmail.com](mailto:puras.he@gmail.com)

## GitHub

[https://github.com/puras/mop](https://github.com/puras/mop)
