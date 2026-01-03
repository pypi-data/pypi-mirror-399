from nextrows.api.extract import build_extract_payload


def test_build_extract_payload_with_schema_dict() -> None:
    request = {
        "type": "text",
        "data": ["example"],
        "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
    }
    payload = build_extract_payload(request)

    assert payload["schema"] == request["schema"]


def test_build_extract_payload_without_schema() -> None:
    request = {"type": "url", "data": ["https://example.com"]}
    payload = build_extract_payload(request)

    assert payload == request
