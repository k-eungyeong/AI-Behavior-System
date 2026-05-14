import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.routers.auth import get_current_user
from app.services.db_service import save_analysis_result
from app.services.model_service import calculate_risk_and_action
from app.services.response_action_service import execute_response_action
from app.services.rag_service import search_response_guide


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

security = HTTPBearer(auto_error=False)


class AnalysisRequest(BaseModel):
    file_path: str


def extract_video_id(file_path: str) -> str:
    filename = Path(file_path).name

    if "_" in filename:
        return filename.split("_")[0]

    return filename


@router.post("/")
async def analyze_video(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        video_id = extract_video_id(request.file_path)

        analysis_mode = os.getenv("ANALYSIS_MODE", "full").lower()

        if analysis_mode == "lightweight":
            from app.services.lightweight_analysis_service import run_lightweight_pipeline

            ai_result = run_lightweight_pipeline(request.file_path)
        else:
            from app.services.ai_service import run_ai_pipeline

            ai_result = run_ai_pipeline(request.file_path)

        behavior_result = ai_result["behavior_result"]
        behavior_confidence = ai_result["behavior_confidence"]

        object_detected = ai_result["object_detected"]
        object_label = ai_result["object_label"]
        object_confidence = ai_result["object_confidence"]

        risk_score, action = calculate_risk_and_action(
            behavior_result=behavior_result,
            behavior_confidence=behavior_confidence,
            object_detected=object_detected,
            object_label=object_label,
            object_confidence=object_confidence
        )

        if risk_score < 30:
            status = "safe"
        elif risk_score < 60:
            status = "warning"
        else:
            status = "danger"

        saved_result = save_analysis_result(
            db=db,
            video_id=video_id,
            user_id=current_user.id,
            camera_name="UPLOAD",
            camera_location="영상 업로드 분석",
            behavior_result=behavior_result,
            behavior_confidence=behavior_confidence,
            object_detected=object_detected,
            object_label=object_label,
            object_confidence=object_confidence,
            risk_score=risk_score,
            action=action
        )

        action_result = execute_response_action(
            action=action,
            video_id=video_id,
            risk_score=risk_score
        )

        rag_guide = search_response_guide(
            object_label=object_label,
            behavior_result=behavior_result,
            action=action,
            risk_score=risk_score
        )

        return {
            "success": True,
            "video_id": saved_result.video_id,
            "user_id": saved_result.user_id,
            "behavior_result": (
                "abnormal"
                if behavior_result == 1
                else "normal"
            ),
            "behavior_confidence": behavior_confidence,
            "object_detected": object_detected,
            "object_label": object_label,
            "object_confidence": object_confidence,
            "risk_score": risk_score,
            "status": status,
            "action": action,
            "action_result": action_result,
            "created_at": saved_result.created_at,
            "camera_name": saved_result.camera_name,
            "camera_location": saved_result.camera_location,
            "analysis_mode": ai_result.get("analysis_mode", analysis_mode),
            "analysis_details": ai_result.get("analysis_details"),
            "rag_guide": rag_guide,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"영상 분석 실패: {str(e)}"
        )
