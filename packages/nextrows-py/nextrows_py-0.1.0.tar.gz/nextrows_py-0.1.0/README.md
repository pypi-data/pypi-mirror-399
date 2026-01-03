# nextrows-py

Python client for the Nextrows Open API.

## Getting Started

### API Key

To use this client, you need a NextRows API key. Create one at:

**NextRows Dashboard**: https://nextrows.com/dashboard/overview

### Documentation

API docs: https://nextrows.com/docs/api

## Installation

```bash
pip install nextrows-py
```

## Development (uv)

```bash
uv venv
uv pip install -e ".[test]"
uv run pytest
```

## Quick Start

```python
from nextrows import Nextrows

client = Nextrows(api_key="sk-nr-your-api-key")
```

## API Methods

### Extract Data

```python
result = client.extract(
    {
        "type": "url",
        "data": ["https://example.com/products"],
        "prompt": "Extract all product names and prices",
    }
)

if result["success"]:
    print(result.get("data"))
```

#### Using Pydantic Schema (Optional)

Install pydantic and pass a model or schema object. The client converts it to JSON Schema.

```bash
pip install "nextrows-py[schema]"
```

```python
from pydantic import BaseModel
from nextrows import Nextrows

class Product(BaseModel):
    name: str
    price: float

client = Nextrows(api_key="sk-nr-your-api-key")

result = client.extract(
    {
        "type": "text",
        "data": ["Product A costs $10, Product B costs $20"],
        "schema": Product,
    }
)
```

### Async Client

```bash
pip install \"nextrows-py[async]\"
```

```python
import asyncio
from nextrows import AsyncNextrows

async def main() -> None:
    async with AsyncNextrows(api_key=\"sk-nr-your-api-key\") as client:
        result = await client.get_credits()
        print(result)

asyncio.run(main())
```

### Run App (JSON)

```python
result = client.run_app_json(
    {
        "appId": "abc123xyz",
        "inputs": [
            {"key": "url", "value": "https://example.com/products"},
            {"key": "maxItems", "value": 10},
        ],
    }
)

if result["success"] and result.get("data"):
    for row in result["data"]:
        print(row)
```

### Run App (Table)

```python
result = client.run_app_table(
    {
        "appId": "abc123xyz",
        "inputs": [{"key": "url", "value": "https://example.com/products"}],
    }
)

if result["success"] and result.get("data"):
    print(result["data"]["columns"])
    for row in result["data"]["tableData"]:
        print(row)
```

### Get Credits

```python
result = client.get_credits()

if result["success"] and result.get("data"):
    print(f"Remaining credits: {result['data']['credits']}")
```

## Configuration

```python
client = Nextrows(
    api_key="sk-nr-your-api-key",
    base_url="https://api.nextrows.com",
    timeout=30.0,
)
```

## Notes

- `timeout` is in seconds (float), default 30s.
- `schema` accepts a JSON Schema dict or a Pydantic model/class with schema methods.
