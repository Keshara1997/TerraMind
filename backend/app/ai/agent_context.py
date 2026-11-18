from dataclasses import dataclass
from sqlalchemy.orm import Session


@dataclass
class AlephAgentContext:
    db: Session
    user_id: str
    project_id: str