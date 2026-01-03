# Crimsy

A lightweight web framework for building APIs in Python, built on top of Starlette with `msgspec` for fast JSON encoding/decoding.

## Features

- 🚀 **Fast**: Uses `msgspec` for ultra-fast JSON encoding/decoding
- 🪶 **Lightweight**: Minimal dependencies (only `starlette` and `msgspec`)
- 🔒 **Fully Typed**: Complete type hints for better IDE support
- 📚 **Auto Documentation**: Automatic OpenAPI schema generation and Swagger UI
- 🎯 **Familiar API**: Similar interface to FastAPI for easy adoption
- ⚡ **All HTTP Methods**: Support for GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS

## Installation

```bash
pip install crimsy  # (when published)
# or for development:
uv sync
```

## Quick Start

```python
import msgspec
from crimsy import Crimsy, Router


class User(msgspec.Struct):
    name: str
    age: int = 0


app = Crimsy()
router = Router(prefix="/users")


@router.get("/")
async def list_users() -> list[User]:
    return [User(name="Alice", age=30), User(name="Bob", age=25)]


@router.post("/")
async def create_user(user: User) -> User:
    # Your code here
    return user


app.add_router(router)
```

Run with:
```bash
uvicorn app:app --reload
```

## Documentation

- **OpenAPI JSON**: Automatically available at `/openapi.json`
- **Swagger UI**: Automatically available at `/docs`

## Examples

See [README_EXAMPLES.md](README_EXAMPLES.md) for comprehensive examples demonstrating all features.

## Development

```bash
# Install dependencies
just install

# Run tests
just test

# Run linting
just lint
```

## License

See LICENSE file.
