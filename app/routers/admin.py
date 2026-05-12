from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, AnalysisResult
from app.routers.auth import get_current_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = db.query(User).all()

    data = []

    for user in users:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        })

    return {
        "success": True,
        "count": len(data),
        "data": data
    }


@router.get("/analysis")
def get_all_analysis_results(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    results = db.query(AnalysisResult).order_by(
        AnalysisResult.created_at.desc()
    ).all()

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


@router.patch("/users/{user_id}/disable")
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return {
            "success": False,
            "message": "사용자를 찾을 수 없습니다."
        }

    user.is_active = False

    db.commit()

    return {
        "success": True,
        "message": "사용자가 비활성화되었습니다."
    }


@router.patch("/users/{user_id}/enable")
def enable_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return {
            "success": False,
            "message": "사용자를 찾을 수 없습니다."
        }

    user.is_active = True

    db.commit()

    return {
        "success": True,
        "message": "사용자가 활성화되었습니다."
    }