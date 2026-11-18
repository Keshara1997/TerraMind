from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.context_builder import build_project_context
from app.ai.factory import get_ai_provider
from app.ai.prompts import (
    GEOSPATIAL_SYSTEM_INSTRUCTIONS,
    build_analysis_prompt,
)
from app.core.config import settings


async def ask_project_question(
    db: Session,
    project_id: UUID,
    question: str,
    start_date: date | None = None,
    end_date: date | None = None,
    area_id: UUID | None = None,
):
    if start_date and end_date and start_date > end_date:
        raise ValueError("Invalid date range")

    context = build_project_context(
        db=db,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        area_id=area_id,
    )

    if context["total_observations"] == 0:
        return {
            "answer": (
                "There are no completed NDVI observations "
                "available for the selected project and period. "
                "Process satellite captures before requesting "
                "a vegetation analysis."
            ),
            "observations_used": 0,
        }

    provider = get_ai_provider()

    prompt = build_analysis_prompt(
        question=question,
        context=context,
    )

    answer = await provider.generate(
        instructions=GEOSPATIAL_SYSTEM_INSTRUCTIONS,
        prompt=prompt,
    )

    return {
        "answer": answer,
        "observations_used": context["total_observations"],
        "model": settings.AI_MODEL,
    }