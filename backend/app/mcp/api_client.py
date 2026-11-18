import httpx

from app.mcp.config import get_mcp_config


class AlephAPIClient:

    def __init__(self):
        self.config = get_mcp_config()

        self.client = httpx.AsyncClient(
            base_url=self.config.api_base_url,
            headers={
                "Authorization": (
                    f"Bearer {self.config.access_token}"
                ),
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(60.0),
        )

    async def get(
        self,
        path: str,
        params: dict | None = None,
    ):
        response = await self.client.get(
            path,
            params=params,
        )

        response.raise_for_status()
        return response.json()

    async def post(
        self,
        path: str,
        payload: dict,
    ):
        response = await self.client.post(
            path,
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()