from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.database.models import User
from app.routers.auth import get_current_user
from app.services.rag_service import search_response_guide


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


class RagGuideRequest(BaseModel):
    object_label: str | None = None
    behavior_result: int | str | None = None
    action: str | None = None
    risk_score: float | None = None


@router.post("/guide")
def get_rag_guide(
    request: RagGuideRequest,
    current_user: User = Depends(get_current_user)
):
    result = search_response_guide(
        object_label=request.object_label,
        behavior_result=request.behavior_result,
        action=request.action,
        risk_score=request.risk_score
    )

    return {
        "success": True,
        "user_id": current_user.id,
        "rag_result": result
    }