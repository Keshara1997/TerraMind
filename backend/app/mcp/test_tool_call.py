import asyncio
import json

from mcp import Client

from app.mcp.server import mcp


async def main():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_ndvi_time_series",
            {
                "project_id": "YOUR_PROJECT_UUID",
                "start_date": "2026-01-01",
                "end_date": "2026-10-31",
            },
        )

        for content in result.content:
            if hasattr(content, "text"):
                print(content.text)

        if result.isError:
            raise RuntimeError("MCP tool call failed")


if __name__ == "__main__":
    asyncio.run(main())