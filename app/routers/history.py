from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.routers.auth import get_current_user
from app.services.db_service import (
    get_all_results,
    get_result_by_video_id
)


router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.get("/")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role == "admin"

    results = get_all_results(
        db=db,
        user_id=current_user.id,
        is_admin=is_admin
    )

    data = []

    for result in results:
        data.append({
            "video_id": result.video_id,
            "user_id": result.user_id,

            "behavior_result": result.behavior_result,
            "behavior_confidence": result.behavior_confidence,

            "object_detected": result.object_detected,
            "object_label": result.object_label,
            "object_confidence": result.object_confidence,

            "risk_score": result.risk_score,
            "action": result.action,

            "created_at": result.created_at
        })

    return {
        "success": True,
        "count": len(data),
        "data": data
    }


@router.get("/{video_id}")
def get_history_detail(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role == "admin"

    result = get_result_by_video_id(
        db=db,
        video_id=video_id,
        user_id=current_user.id,
        is_admin=is_admin
    )

    if not result:
        return {
            "success": False,
            "message": "분석 기록을 찾을 수 없습니다."
        }

    return {
        "success": True,
        "data": {
            "video_id": result.video_id,
            "user_id": result.user_id,

            "behavior_result": result.behavior_result,
            "behavior_confidence": result.behavior_confidence,

            "object_detected": result.object_detected,
            "object_label": result.object_label,
            "object_confidence": result.object_confidence,

            "risk_score": result.risk_score,
            "action": result.action,

            "created_at": result.created_at
        }
    }