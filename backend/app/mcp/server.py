import json
from datetime import date

import httpx
from mcp.server import MCPServer

from app.mcp.api_client import AlephAPIClient
from app.mcp.prompts import (
    environmental_report_prompt,
    vegetation_analysis_prompt,
)

mcp = MCPServer(
    "Aleph Next Geospatial MCP",
    log_level="INFO",
)


async def execute_api_request(method, path, params=None, payload=None):
    client = AlephAPIClient()

    try:
        if method == "GET":
            result = await client.get(path, params=params)
        elif method == "POST":
            result = await client.post(path, payload=payload or {})
        else:
            raise ValueError("Unsupported API method")

        return json.dumps(result, indent=2, default=str)

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Aleph API returned HTTP {exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Unable to connect to the Aleph Next API"
        ) from exc

    finally:
        await client.close()


@mcp.tool()
async def get_ndvi_time_series(
    project_id: str,
    start_date: str,
    end_date: str,
    area_id: str = "",
) -> str:
    """
    Retrieve verified NDVI observations for an Aleph Next project.

    Use this tool when the user asks about vegetation trends,
    NDVI statistics or historical satellite observations.
    """

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError("start_date must not be after end_date")

    params = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }

    if area_id:
        params["area_id"] = area_id

    return await execute_api_request(
        "GET",
        f"/analysis/projects/{project_id}/ndvi-time-series",
        params=params,
    )


@mcp.tool()
async def ask_geospatial_question(
    project_id: str,
    question: str,
    start_date: str = "",
    end_date: str = "",
    area_id: str = "",
) -> str:
    """
    Ask Aleph Next AI to analyse a project's verified geospatial data.

    Use this tool for natural-language questions about vegetation,
    NDVI trends and satellite analysis.
    """

    if not question.strip() or len(question) > 2000:
        raise ValueError(
            "Question must contain between 1 and 2000 characters"
        )

    payload = {
        "question": question,
    }

    if start_date:
        payload["start_date"] = date.fromisoformat(
            start_date
        ).isoformat()

    if end_date:
        payload["end_date"] = date.fromisoformat(
            end_date
        ).isoformat()

    if start_date and end_date and start_date > end_date:
        raise ValueError("Invalid date range")

    if area_id:
        payload["area_id"] = area_id

    return await execute_api_request(
        "POST",
        f"/ai/projects/{project_id}/ask",
        payload=payload,
    )


@mcp.tool()
async def generate_environmental_report(
    project_id: str,
    start_date: str,
    end_date: str,
    area_id: str = "",
) -> str:
    """
    Generate an environmental monitoring report.

    This may incur AI provider costs. Only call it when the user
    explicitly requests a report.
    """

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError("Invalid report date range")

    payload = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }

    if area_id:
        payload["area_id"] = area_id

    return await execute_api_request(
        "POST",
        f"/ai/projects/{project_id}/environmental-report",
        payload=payload,
    )


@mcp.resource("aleph://capabilities")
def aleph_capabilities() -> str:
    """Describe the available Aleph Next geospatial capabilities."""

    return json.dumps({
        "application": "Aleph Next",
        "capabilities": [
            "NDVI time-series retrieval",
            "Geospatial question answering",
            "Environmental report generation",
        ],
        "data_source": "Authenticated Aleph Next API",
        "authorization": "Existing user JWT",
    }, indent=2)


@mcp.prompt()
def analyse_vegetation(
    project_id: str,
    start_date: str,
    end_date: str,
) -> str:
    """Create a reusable vegetation-analysis prompt."""

    date.fromisoformat(start_date)
    date.fromisoformat(end_date)

    return vegetation_analysis_prompt(
        project_id,
        start_date,
        end_date,
    )


@mcp.prompt()
def create_environmental_report(
    project_id: str,
) -> str:
    """Create a reusable environmental report prompt."""

    return environmental_report_prompt(project_id)


if __name__ == "__main__":
    # Default transport is stdio.
    # The MCP client launches this process.
    mcp.run()