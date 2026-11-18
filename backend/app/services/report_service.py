from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.context_builder import build_project_context
from app.ai.factory import get_ai_provider
from app.ai.prompts import GEOSPATIAL_SYSTEM_INSTRUCTIONS


async def generate_environmental_report(
    db: Session,
    project_id: UUID,
    start_date: date,
    end_date: date,
    area_id: UUID | None = None,
):
    if start_date > end_date:
        raise ValueError("Invalid report date range")

    context = build_project_context(
        db=db,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        area_id=area_id,
    )

    if not context["ndvi_observations"]:
        raise ValueError(
            "No completed NDVI observations are available"
        )

    provider = get_ai_provider()

    instructions = GEOSPATIAL_SYSTEM_INSTRUCTIONS + """
    Generate a structured environmental monitoring report.

    Include:
    1. Executive summary
    2. Data coverage and observation dates
    3. NDVI trend analysis
    4. Significant changes
    5. Data limitations
    6. Recommendations for further investigation

    Clearly distinguish measurements from interpretation.
    Do not invent statistics or environmental causes.
    """

    import json

    prompt = (
        "Generate an environmental monitoring report using "
        "the following project data:\n\n"
        + json.dumps(context, indent=2, default=str)
    )

    report = await provider.generate(
        instructions=instructions,
        prompt=prompt,
    )

    return {
        "project_id": project_id,
        "title": "Environmental Monitoring Report",
        "period_start": start_date,
        "period_end": end_date,
        "observations_used": context["total_observations"],
        "report": report,
    }