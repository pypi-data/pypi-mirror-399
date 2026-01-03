from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

from nextrows.api.apps import run_app_json, run_app_table
from nextrows.api.credits import get_credits
from nextrows.api.extract import build_extract_payload, extract
from nextrows.types import (
    ExtractRequest,
    ExtractResponse,
    GetCreditsResponse,
    RunAppJsonRequest,
    RunAppJsonResponse,
    RunAppTableRequest,
    RunAppTableResponse,
)

BASE_URL = "https://api.nextrows.com"


@dataclass(frozen=True)
class NextrowsOptions:
    api_key: str
    base_url: str = BASE_URL
    timeout: float = 30.0


class Nextrows:
    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def extract(self, request: ExtractRequest) -> ExtractResponse:
        return extract(self.session, self.base_url, request, self.timeout)

    def get_credits(self) -> GetCreditsResponse:
        return get_credits(self.session, self.base_url, self.timeout)

    def run_app_json(self, request: RunAppJsonRequest) -> RunAppJsonResponse:
        return run_app_json(self.session, self.base_url, request, self.timeout)

    def run_app_table(self, request: RunAppTableRequest) -> RunAppTableResponse:
        return run_app_table(self.session, self.base_url, request, self.timeout)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "Nextrows":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class AsyncNextrows:
    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        client: Optional[object] = None,
    ) -> None:
        try:
            import httpx
        except ImportError as exc:
            raise ImportError(
                "AsyncNextrows requires httpx. Install with `pip install nextrows-py[async]`."
            ) from exc

        self._httpx = httpx
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = client or httpx.AsyncClient()
        self.client.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    async def extract(self, request: ExtractRequest) -> ExtractResponse:
        payload = build_extract_payload(request)
        response = await self.client.post(
            f"{self.base_url}/v1/extract",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    async def get_credits(self) -> GetCreditsResponse:
        response = await self.client.get(
            f"{self.base_url}/v1/credits", timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    async def run_app_json(self, request: RunAppJsonRequest) -> RunAppJsonResponse:
        response = await self.client.post(
            f"{self.base_url}/v1/apps/run/json",
            json=request,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    async def run_app_table(self, request: RunAppTableRequest) -> RunAppTableResponse:
        response = await self.client.post(
            f"{self.base_url}/v1/apps/run/table",
            json=request,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "AsyncNextrows":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
