from agents import RunContextWrapper, function_tool

from app.ai.agent_context import AlephAgentContext


@function_tool
async def get_project_ndvi_history(
    ctx: RunContextWrapper[AlephAgentContext],
    start_date: str,
    end_date: str,
    area_id: str = "",
) -> dict:
    """
    Retrieve NDVI time-series measurements for the authenticated project.

    Use this tool when the user asks about vegetation trends,
    historical NDVI measurements, or vegetation changes.
    """

    context = ctx.context

    # Import the existing service from Step 13.
    from app.services.time_series_service import get_ndvi_time_series

    # Important:
    # Adapt this call to the actual signature and return type
    # of your existing Step 13 service.
    result = await get_ndvi_time_series(
        db=context.db,
        project_id=context.project_id,
        user_id=context.user_id,
        start_date=start_date,
        end_date=end_date,
        area_id=area_id or None,
    )

    return result


@function_tool
async def get_project_environmental_insights(
    ctx: RunContextWrapper[AlephAgentContext],
) -> dict:
    """
    Retrieve environmental analysis information for the current project.

    Use this tool when the user asks for a project overview
    or a summary of available environmental measurements.
    """

    context = ctx.context

    from app.services.time_series_service import get_project_ndvi_summary

    # Implement or adapt this service using your existing models.
    result = await get_project_ndvi_summary(
        db=context.db,
        project_id=context.project_id,
        user_id=context.user_id,
    )

    return result