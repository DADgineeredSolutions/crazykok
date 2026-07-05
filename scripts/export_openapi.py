#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from starlette.requests import Request

from backend.app.main import app
from backend.app.openapi_contract import public_openapi


def canonical_document() -> dict:
    os.environ["PUBLIC_API_BASE_URL"] = "https://api.crazykok.local/v1"
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "https",
            "server": ("api.crazykok.local", 443),
            "path": "/v1/openapi.json",
            "headers": [(b"host", b"api.crazykok.local")],
            "app": app,
        }
    )
    return public_openapi(app, request)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the generated public OpenAPI contract")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(canonical_document(), indent=2, sort_keys=True) + "\n"
    if not args.output:
        print(rendered, end="")
        return 0
    if args.check:
        if not args.output.exists() or args.output.read_text() != rendered:
            print(f"{args.output} is stale; regenerate it with scripts/export_openapi.py --output {args.output}")
            return 1
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
