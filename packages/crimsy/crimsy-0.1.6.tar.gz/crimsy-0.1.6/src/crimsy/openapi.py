"""OpenAPI schema generation and documentation endpoints."""

import inspect
from typing import Any

import msgspec
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from crimsy.params import ParamInfo, ParamType, is_msgspec_struct


def get_openapi_route(app: Any, path: str) -> Route:
    """Create the OpenAPI JSON endpoint.

    Args:
        app: Ethereal application instance
        path: URL path for the endpoint

    Returns:
        Starlette Route for OpenAPI JSON
    """

    async def openapi_handler(request: Request) -> JSONResponse:
        schema = app.openapi_schema()
        return JSONResponse(schema)

    return Route(path, openapi_handler, methods=["GET"])


def get_swagger_ui_route(app: Any, docs_path: str, openapi_path: str) -> Route:
    """Create the Swagger UI documentation endpoint.

    Args:
        app: Ethereal application instance
        docs_path: URL path for Swagger UI
        openapi_path: URL path for OpenAPI JSON

    Returns:
        Starlette Route for Swagger UI
    """

    async def swagger_ui_handler(request: Request) -> HTMLResponse:
        # Note: For production use, consider either:
        # 1. Bundling these assets locally
        # 2. Using correct SRI hashes from the Swagger UI distribution
        # 3. Self-hosting the Swagger UI files
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{app.title} - Swagger UI</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css">
            <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.9.0/favicon-32x32.png" sizes="32x32" />
            <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.9.0/favicon-16x16.png" sizes="16x16" />
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {{
                    window.ui = SwaggerUIBundle({{
                        url: "{openapi_path}",
                        dom_id: '#swagger-ui',
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout",
                        deepLinking: true,
                        showExtensions: true,
                        showCommonExtensions: true
                    }});
                }};
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    return Route(docs_path, swagger_ui_handler, methods=["GET"])


def generate_openapi_schema(app: Any) -> dict[str, Any]:
    """Generate OpenAPI 3.0 schema for the application.

    Args:
        app: Crimsy application instance

    Returns:
        OpenAPI schema dictionary
    """
    paths: dict[str, Any] = {}

    # Iterate through all routers
    for router in app._routers:
        for route in router.routes:
            # Get the path with router prefix
            full_path = router.prefix.rstrip("/") + route.path

            # Get the original endpoint and parameters
            endpoint = getattr(route.endpoint, "_original_endpoint", None)
            params = getattr(route.endpoint, "_params", [])
            # Get the original methods list (before Starlette adds HEAD for GET)
            original_methods = getattr(route.endpoint, "_original_methods", None)

            if endpoint is None:
                continue

            # Use original methods if available, otherwise fallback to route.methods
            methods_to_document = (
                original_methods if original_methods else route.methods or []
            )

            # Get endpoint metadata
            operation = generate_operation(endpoint, params, methods_to_document, app)

            # Add to paths
            if full_path not in paths:
                paths[full_path] = {}

            for method in methods_to_document:
                paths[full_path][method.lower()] = operation

    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": app.title,
            "version": app.version,
        },
        "paths": paths,
    }

    return schema


def generate_operation(
    endpoint: Any, params: list[ParamInfo], methods: list[str], app: Any
) -> dict[str, Any]:
    """Generate OpenAPI operation object for an endpoint.

    Args:
        endpoint: Endpoint function
        params: List of parameter information
        methods: HTTP methods
        app: Crimsy application instance

    Returns:
        OpenAPI operation dictionary
    """
    operation: dict[str, Any] = {
        "responses": {
            "200": {
                "description": "Successful response",
            }
        },
    }

    # Add summary and description from docstring
    if endpoint.__doc__:
        operation["summary"] = endpoint.__doc__.strip().split("\n")[0]
        operation["description"] = endpoint.__doc__.strip()

    # Add parameters
    parameters = []
    request_body = None

    for param in params:
        if param.param_type == ParamType.DEPENDENCY:
            # Dependencies don't show up in OpenAPI parameters
            pass
        elif param.param_type == ParamType.REQUEST:
            # Request parameters don't show up in OpenAPI parameters (auto-injected)
            pass
        elif param.param_type == ParamType.QUERY:
            param_schema = get_parameter_schema(param)
            parameters.append(
                {
                    "name": param.name,
                    "in": "query",
                    "required": param.is_required,
                    "schema": param_schema,
                }
            )
        elif param.param_type == ParamType.BODY:
            # Body parameters
            schema = get_parameter_schema(param)
            request_body = {
                "required": param.is_required,
                "content": {
                    "application/json": {
                        "schema": schema,
                    }
                },
            }
        elif param.param_type == ParamType.PATH:
            param_schema = get_parameter_schema(param)
            parameters.append(
                {
                    "name": param.name,
                    "in": "path",
                    "required": True,
                    "schema": param_schema,
                }
            )

    if parameters:
        operation["parameters"] = parameters

    if request_body:
        operation["requestBody"] = request_body

    # Add response schema
    sig = inspect.signature(endpoint)
    if sig.return_annotation is not inspect.Signature.empty:
        return_schema = get_type_schema(sig.return_annotation)
        operation["responses"]["200"]["content"] = {
            "application/json": {
                "schema": return_schema,
            }
        }

    return operation


def get_parameter_schema(param: ParamInfo) -> dict[str, Any]:
    """Get OpenAPI schema for a parameter.

    Args:
        param: Parameter information

    Returns:
        OpenAPI schema dictionary
    """
    return get_type_schema(param.annotation)


def get_type_schema(annotation: type[Any]) -> dict[str, Any]:
    """Get OpenAPI schema for a type annotation.

    Args:
        annotation: Type annotation

    Returns:
        OpenAPI schema dictionary
    """
    # Handle msgspec.Struct
    if is_msgspec_struct(annotation):
        return get_msgspec_struct_schema(annotation)

    # Handle basic types
    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation in (dict, Any):
        return {"type": "object"}
    if annotation is list:
        return {"type": "array", "items": {}}

    # Handle generic types
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        args = getattr(annotation, "__args__", ())
        if args:
            return {"type": "array", "items": get_type_schema(args[0])}
        return {"type": "array", "items": {}}

    if origin is dict:
        return {"type": "object"}

    # Default
    return {"type": "string"}


def get_msgspec_struct_schema(struct_type: type[msgspec.Struct]) -> dict[str, Any]:
    """Get OpenAPI schema for a msgspec.Struct type.

    Args:
        struct_type: msgspec.Struct type

    Returns:
        OpenAPI schema dictionary
    """
    properties: dict[str, Any] = {}
    required = []

    # Get struct fields
    for field in msgspec.structs.fields(struct_type):
        field_schema = get_type_schema(field.type)
        properties[field.name] = field_schema

        # Check if field is required (no default value)
        if (
            field.default is msgspec.NODEFAULT
            and field.default_factory is msgspec.NODEFAULT
        ):
            required.append(field.name)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }

    if required:
        schema["required"] = required

    return schema
