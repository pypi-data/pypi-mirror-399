from __future__ import annotations

from typing import Any, Dict

import requests

from nextrows.types import ExtractRequest, ExtractResponse, ExtractSchema, JsonSchema


def _convert_schema(schema: ExtractSchema) -> JsonSchema:
    if isinstance(schema, dict):
        return schema

    model_json_schema = getattr(schema, "model_json_schema", None)
    if callable(model_json_schema):
        return model_json_schema()

    legacy_schema = getattr(schema, "schema", None)
    if callable(legacy_schema):
        return legacy_schema()

    raise ValueError(
        "Schema must be a JSON schema dict or a pydantic model with schema methods."
    )


def build_extract_payload(request: ExtractRequest) -> Dict[str, Any]:
    if "schema" in request and request["schema"] is not None:
        return {**request, "schema": _convert_schema(request["schema"])}
    return dict(request)


def extract(
    session: requests.Session,
    base_url: str,
    request: ExtractRequest,
    timeout: float,
) -> ExtractResponse:
    payload = build_extract_payload(request)

    response = session.post(f"{base_url}/v1/extract", json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()
