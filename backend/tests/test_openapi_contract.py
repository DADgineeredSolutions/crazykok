import json
from pathlib import Path

import yaml
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
BASELINE = Path(__file__).resolve().parents[2] / "docs" / "api" / "openapi" / "openapi.json"


def test_contract_is_discoverable_from_the_api_root():
    root = client.get("/v1").json()
    description_url = root["_links"]["api-description"]["href"]
    description = client.get(description_url)

    assert description.status_code == 200
    assert description.headers["content-type"].startswith("application/hal+json")
    assert description.json()["_links"]["documentation"]["href"].startswith("https://api-docs.")
    assert len(description.json()["_links"]["openapi"]) == 2


def test_json_and_yaml_are_equivalent_cacheable_public_contracts():
    json_response = client.get("/v1/openapi.json")
    yaml_response = client.get("/v1/openapi.yaml")

    assert json_response.status_code == 200
    assert yaml_response.status_code == 200
    assert json_response.json() == yaml.safe_load(yaml_response.text)
    assert json_response.headers["etag"]
    assert "public" in json_response.headers["cache-control"]
    assert client.get(
        "/v1/openapi.json", headers={"If-None-Match": json_response.headers["etag"]}
    ).status_code == 304

    document = json_response.json()
    assert document["openapi"].startswith("3.1.")
    assert document["jsonSchemaDialect"].endswith("2020-12/schema")
    assert not any(path.startswith("/internal/") for path in document["paths"])
    assert "/v1/opportunities" in document["paths"]
    assert "/venues" in document["paths"]
    parameters = document["paths"]["/v1/opportunities"]["get"]["parameters"]
    sort = next(parameter for parameter in parameters if parameter["name"] == "sort")
    page = next(parameter for parameter in parameters if parameter["name"] == "page")
    assert "event_date" in sort["schema"]["enum"]
    assert page["schema"]["maximum"] == 1_000_000


def test_every_documented_operation_has_a_stable_unique_identifier():
    document = client.get("/v1/openapi.json").json()
    operations = [
        operation
        for path in document["paths"].values()
        for method, operation in path.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    identifiers = [operation["operationId"] for operation in operations]

    assert len(identifiers) == len(set(identifiers))
    assert all(operation.get("summary") for operation in operations)
    assert all(operation.get("tags") for operation in operations)


def test_contract_covers_every_intentionally_public_route():
    document = client.get("/v1/openapi.json").json()
    documented = {
        (path, method.upper())
        for path, path_item in document["paths"].items()
        for method in path_item
        if method in {"get", "post", "put", "patch", "delete"}
    }
    routes = {
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.include_in_schema
        and not route.path.startswith("/internal/")
        for method in route.methods
        if method != "HEAD"
    }
    assert documented == routes


def test_component_schemas_are_public_and_resolve_with_defs():
    catalog = client.get("/v1/schemas")
    assert catalog.status_code == 200
    assert catalog.json()["count"] > 0
    first = catalog.json()["_links"]["item"][0]

    schema = client.get(first["href"])
    assert schema.status_code == 200
    assert schema.headers["content-type"].startswith("application/schema+json")
    payload = json.loads(schema.content)
    assert payload["$ref"].startswith("#/$defs/")
    assert payload["$defs"]
    assert "#/components/schemas/" not in schema.text


def test_legacy_framework_docs_redirect_to_the_canonical_surfaces():
    assert client.get("/openapi.json", follow_redirects=False).headers["location"] == "/v1/openapi.json"
    assert client.get("/docs", follow_redirects=False).headers["location"].startswith("https://api-docs.")


def test_generated_contract_matches_the_reviewed_baseline():
    baseline = json.loads(BASELINE.read_text())
    current = client.get("/v1/openapi.json").json()
    # Deployment origin is intentionally request-aware and is not contract drift.
    current["servers"] = baseline["servers"]
    assert current == baseline
