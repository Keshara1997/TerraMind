from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from openai import APIError, APITimeoutError, RateLimitError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.ai import AIQuestionRequest, AIQuestionResponse
from app.services.ai_analysis_service import ask_project_question
from app.services.project_service import ProjectService

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


@router.post(
    "/projects/{project_id}/ask",
    response_model=AIQuestionResponse,
)
async def ask_geospatial_question(
    project_id: UUID,
    payload: AIQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        if payload.start_date and payload.end_date:
            if payload.start_date > payload.end_date:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date range",
                )

        # Enforce project ownership before retrieving any data.
        ProjectService(db).get_project(
            project_id,
            current_user.id,
        )

        # If area_id is supplied, verify that it belongs to this
        # project and that the current user can access it.
        if payload.area_id:
            from app.models.area import Area

            area = db.query(Area).filter(
                Area.id == payload.area_id,
                Area.project_id == project_id,
            ).first()

            if not area:
                raise HTTPException(
                    status_code=404,
                    detail="Area not found in this project",
                )

        result = await ask_project_question(
            db=db,
            project_id=project_id,
            question=payload.question,
            start_date=payload.start_date,
            end_date=payload.end_date,
            area_id=payload.area_id,
        )

        return AIQuestionResponse(
            project_id=project_id,
            question=payload.question,
            answer=result["answer"],
            observations_used=result["observations_used"],
            model=result.get("model", "not-used"),
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (APITimeoutError, RateLimitError):
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable",
        )

    except APIError:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an error",
        )



        from app.schemas.report import (
    EnvironmentalReportRequest,
    EnvironmentalReportResponse,
)
from app.services.report_service import (
    generate_environmental_report,
)


@router.post(
    "/projects/{project_id}/environmental-report",
    response_model=EnvironmentalReportResponse,
)
async def create_environmental_report(
    project_id: UUID,
    payload: EnvironmentalReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ProjectService(db).get_project(
        project_id,
        current_user.id,
    )

    if payload.area_id:
        from app.models.area import Area

        area = db.query(Area).filter(
            Area.id == payload.area_id,
            Area.project_id == project_id,
        ).first()

        if not area:
            raise HTTPException(
                status_code=404,
                detail="Area not found in this project",
            )

    try:
        return await generate_environmental_report(
            db=db,
            project_id=project_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            area_id=payload.area_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc