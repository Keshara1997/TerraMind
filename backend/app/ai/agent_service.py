from agents import Runner

from app.ai.agent import geospatial_agent
from app.ai.agent_context import AlephAgentContext


async def run_geospatial_agent(
    db,
    user_id: str,
    project_id: str,
    question: str,
) -> str:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if len(question) > 4000:
        raise ValueError("Question cannot exceed 4000 characters.")

    context = AlephAgentContext(
        db=db,
        user_id=str(user_id),
        project_id=str(project_id),
    )

    result = await Runner.run(
        geospatial_agent,
        question.strip(),
        context=context,
    )

    return str(result.final_output)