from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_request_id_header_is_returned(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert "x-request-id" in {k.lower() for k in response.headers}
