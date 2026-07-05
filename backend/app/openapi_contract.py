from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from urllib.parse import quote

import yaml
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response
from fastapi.routing import APIRoute

from .hypermedia import HALJSONResponse, HALLink, HALResource, api_url, public_api_base


router = APIRouter(prefix="/v1", tags=["API contract"])


def api_docs_origin() -> str:
    return os.getenv("API_DOCS_ORIGIN", "https://api-docs.crazykok.local").rstrip("/")


def _public_routes(app: FastAPI) -> list[APIRoute]:
    return [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.include_in_schema
        and not route.path.startswith("/internal/")
    ]


def _server_url(request: Request) -> str:
    base = public_api_base(request)
    return base.removesuffix("/v1")


def _without_query_nullability(schema: dict) -> dict:
    """OpenAPI query parameters are omitted, not sent as a literal null."""
    if "anyOf" not in schema:
        return schema
    concrete = [candidate for candidate in schema["anyOf"] if candidate.get("type") != "null"]
    if len(concrete) != 1:
        return schema
    replacement = {**schema, **concrete[0]}
    replacement.pop("anyOf", None)
    return replacement


def public_openapi(app: FastAPI, request: Request) -> dict:
    """Build the public contract from the routes that implement it.

    This is deliberately generated rather than hand-maintained. The committed
    snapshot is a compatibility baseline, not a second source of truth.
    """

    document = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=(
            "The public Crazy Kok HTTP API. Canonical versioned resources use "
            "HAL for navigation and RFC 9457-style problem responses for errors."
        ),
        routes=_public_routes(app),
        tags=[
            {"name": "API v1", "description": "Canonical discoverable HAL resources."},
            {"name": "API contract", "description": "Machine-readable API and schema discovery."},
            {"name": "Health", "description": "Deployment health checks."},
            {"name": "Legacy", "description": "Compatibility routes pending migration to the canonical API."},
            {"name": "venues", "description": "Venue management resources."},
            {"name": "venue imports", "description": "Reviewed venue research imports."},
        ],
    )
    document["servers"] = [{"url": _server_url(request), "description": "Current API deployment"}]
    document["externalDocs"] = {"description": "Interactive API reference", "url": api_docs_origin()}
    document["jsonSchemaDialect"] = "https://json-schema.org/draft/2020-12/schema"
    document.setdefault("components", {}).setdefault("schemas", {})["Problem"] = {
        "type": "object",
        "required": ["type", "title", "status", "detail", "instance"],
        "properties": {
            "type": {"type": "string", "format": "uri-reference"},
            "title": {"type": "string"},
            "status": {"type": "integer"},
            "detail": {"type": "string"},
            "instance": {"type": "string", "format": "uri-reference"},
            "errors": {"type": "array", "items": {"type": "object"}},
        },
    }
    for path, path_item in document["paths"].items():
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            if not operation.get("tags"):
                operation["tags"] = ["Health" if path == "/health" else "Legacy"]
            for parameter in operation.get("parameters", []):
                if parameter.get("in") == "query":
                    parameter["schema"] = _without_query_nullability(parameter.get("schema", {}))
            if path == "/v1" or path.startswith("/v1/"):
                for status, response in operation.get("responses", {}).items():
                    if str(status).startswith(("4", "5")):
                        response["content"] = {
                            "application/problem+json": {
                                "schema": {"$ref": "#/components/schemas/Problem"}
                            }
                        }
    return document


def _encoded(document: dict, media_type: str) -> bytes:
    if media_type == "application/yaml":
        return yaml.safe_dump(document, sort_keys=False, allow_unicode=True).encode()
    return json.dumps(document, indent=2, sort_keys=True).encode()


def _contract_response(request: Request, payload: bytes, media_type: str) -> Response:
    etag = f'"{hashlib.sha256(payload).hexdigest()}"'
    headers = {
        "Cache-Control": "public, max-age=300, must-revalidate",
        "ETag": etag,
        "Vary": "Accept, Host, X-Forwarded-Host, X-Forwarded-Prefix, X-Forwarded-Proto",
    }
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(payload, media_type=media_type, headers=headers)


class APIDescription(HALResource):
    openapi_version: str


@router.get(
    "/api-description",
    response_model=APIDescription,
    response_model_exclude_none=True,
    response_class=HALJSONResponse,
    name="api-v1-description",
)
def api_description(request: Request) -> APIDescription:
    return APIDescription(
        openapi_version=request.app.openapi_version,
        links={
            "self": HALLink(href=api_url(request, "api-description")),
            "openapi": [
                HALLink(href=api_url(request, "openapi.json")),
                HALLink(href=api_url(request, "openapi.yaml")),
            ],
            "schemas": HALLink(href=api_url(request, "schemas")),
            "documentation": HALLink(href=api_docs_origin()),
        },
    )


@router.get(
    "/openapi.json",
    response_class=Response,
    name="api-v1-openapi-json",
    summary="Download the canonical OpenAPI document as JSON",
    responses={200: {"content": {"application/json": {"schema": {"type": "object"}}}}},
)
def openapi_json(request: Request) -> Response:
    return _contract_response(
        request,
        _encoded(public_openapi(request.app, request), "application/json"),
        "application/json",
    )


@router.get(
    "/openapi.yaml",
    response_class=Response,
    name="api-v1-openapi-yaml",
    summary="Download the canonical OpenAPI document as YAML",
    responses={200: {"content": {"application/yaml": {"schema": {"type": "object"}}}}},
)
def openapi_yaml(request: Request) -> Response:
    return _contract_response(
        request,
        _encoded(public_openapi(request.app, request), "application/yaml"),
        "application/yaml",
    )


@router.get("/schemas", response_class=HALJSONResponse, name="api-v1-schema-catalog")
def schema_catalog(request: Request) -> dict:
    document = public_openapi(request.app, request)
    names = sorted(document.get("components", {}).get("schemas", {}))
    return {
        "count": len(names),
        "_links": {
            "self": {"href": api_url(request, "schemas")},
            "item": [
                {"href": api_url(request, f"schemas/{quote(name, safe='')}"), "title": name}
                for name in names
            ],
            "openapi": {"href": api_url(request, "openapi.json")},
        },
    }


@router.get(
    "/schemas/{schema_name}",
    response_class=Response,
    name="api-v1-schema",
    summary="Download one public component as a standalone JSON Schema",
    responses={
        200: {"content": {"application/schema+json": {"schema": {"type": "object"}}}},
        404: {"description": "Schema not found"},
    },
)
def component_schema(request: Request, schema_name: str) -> Response:
    document = public_openapi(request.app, request)
    components = document.get("components", {}).get("schemas", {})
    if schema_name not in components:
        raise HTTPException(status_code=404, detail="Public schema not found")
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": api_url(request, f"schemas/{quote(schema_name, safe='')}"),
        "$ref": f"#/$defs/{schema_name}",
        "$defs": deepcopy(components),
    }
    # OpenAPI component references point at components/schemas. Standalone JSON
    # Schema uses $defs, so rewrite those local references recursively.
    serialized = json.dumps(schema).replace("#/components/schemas/", "#/$defs/")
    return _contract_response(request, serialized.encode(), "application/schema+json")
