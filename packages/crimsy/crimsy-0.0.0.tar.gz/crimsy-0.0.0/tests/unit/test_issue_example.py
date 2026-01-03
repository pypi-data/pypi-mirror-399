"""Test the exact example from the issue."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Router


class User(msgspec.Struct):
    """User model."""

    name: str


async def test_issue_example() -> None:
    """Test the exact example from the issue using GET with query params."""
    app = Crimsy()

    router = Router(prefix="/users")

    @router.get("/")
    async def handler(user: User, name: str) -> User:
        # users code implementation goes here
        return User(name=f"{user.name} and {name}")

    app.add_router(router)

    # Test the application with GET request
    # Per the issue: "the application will expect a valid encoded User and name
    # to be in the query parameters"
    client = TestClient(app)

    import json

    user_json = json.dumps({"name": "Alice"})
    response = client.get(f"/users/?user={user_json}&name=Bob")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice and Bob"


async def test_openapi_generation_for_issue_example() -> None:
    """Test that OpenAPI schema is generated correctly."""
    app = Crimsy()

    router = Router(prefix="/users")

    @router.post("/")
    async def handler(user: User, name: str) -> User:
        return User(name=f"{user.name} and {name}")

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Verify basic structure
    assert schema["openapi"] == "3.0.0"
    assert "paths" in schema
    assert "/users/" in schema["paths"]

    # Verify the endpoint is documented
    post_endpoint = schema["paths"]["/users/"]["post"]
    assert "requestBody" in post_endpoint
    assert "parameters" in post_endpoint

    # Check that name parameter is in query
    params = post_endpoint["parameters"]
    assert any(p["name"] == "name" and p["in"] == "query" for p in params)

    # Check that user is in request body
    assert "application/json" in post_endpoint["requestBody"]["content"]
