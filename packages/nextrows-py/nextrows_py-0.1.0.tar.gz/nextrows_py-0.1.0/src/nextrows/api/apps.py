from __future__ import annotations

import requests

from nextrows.types import RunAppJsonRequest, RunAppJsonResponse, RunAppTableRequest, RunAppTableResponse


def run_app_json(
    session: requests.Session,
    base_url: str,
    request: RunAppJsonRequest,
    timeout: float,
) -> RunAppJsonResponse:
    response = session.post(
        f"{base_url}/v1/apps/run/json",
        json=request,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def run_app_table(
    session: requests.Session,
    base_url: str,
    request: RunAppTableRequest,
    timeout: float,
) -> RunAppTableResponse:
    response = session.post(
        f"{base_url}/v1/apps/run/table",
        json=request,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
