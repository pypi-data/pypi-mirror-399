from __future__ import annotations

import requests

from nextrows.types import GetCreditsResponse


def get_credits(
    session: requests.Session,
    base_url: str,
    timeout: float,
) -> GetCreditsResponse:
    response = session.get(f"{base_url}/v1/credits", timeout=timeout)
    response.raise_for_status()
    return response.json()
