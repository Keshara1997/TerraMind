from agents import Agent

from app.ai.agent_prompts import ALEPH_AGENT_INSTRUCTIONS
from app.ai.agent_tools import (
    get_project_ndvi_history,
    get_project_environmental_insights,
)
from app.core.config import settings


geospatial_agent = Agent(
    name="Aleph Geospatial Agent",
    instructions=ALEPH_AGENT_INSTRUCTIONS,
    model=settings.AI_MODEL,
    tools=[
        get_project_ndvi_history,
        get_project_environmental_insights,
    ],
)