from datetime import datetime, timedelta
import uuid

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.routers.auth import get_current_user
from app.services.db_service import save_analysis_result
from app.services.model_service import calculate_risk_and_action
from app.services.notification_service import send_discord_alert
from app.services.rag_service import search_response_guide
from app.services.object_detection_service import (
    model,
    DANGEROUS_CLASSES,
    CONF_THRESHOLD
)


router = APIRouter(
    prefix="/realtime",
    tags=["Realtime"]
)

LAST_SAVED_DETECTION = {}

DUPLICATE_BLOCK_SECONDS = 10


@router.get("/status")
def realtime_status():
    return {
        "status": "success",
        "message": "Realtime router is connected"
    }


def can_save_detection(label: str, camera_name: str) -> bool:
    now = datetime.now()

    key = f"{camera_name}:{label}"

    last_saved_time = LAST_SAVED_DETECTION.get(key)

    if last_saved_time is None:
        LAST_SAVED_DETECTION[key] = now
        return True

    elapsed = now - last_saved_time

    if elapsed >= timedelta(seconds=DUPLICATE_BLOCK_SECONDS):
        LAST_SAVED_DETECTION[key] = now
        return True

    return False


@router.post("/detect")
async def realtime_detect(
    file: UploadFile = File(...),
    camera_name: str = Form("CAM-01"),
    camera_location: str = Form("실시간 웹캠"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return {
                "success": False,
                "message": "프레임 디코딩 실패"
            }

        results = model(frame, verbose=False)

        detections = []

        best_label = None
        best_conf = 0.0

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls_id].lower()

                if label in DANGEROUS_CLASSES and conf >= CONF_THRESHOLD:
                    detections.append({
                        "label": label,
                        "confidence": round(conf, 4)
                    })

                    if conf > best_conf:
                        best_label = label
                        best_conf = conf

        saved_log = None
        skipped_duplicate = False
        rag_guide = None

        if best_label is not None:
            behavior_result = 0
            behavior_confidence = 0.0
            object_detected = True
            object_label = best_label
            object_confidence = round(best_conf, 4)

            risk_score, action = calculate_risk_and_action(
                behavior_result=behavior_result,
                behavior_confidence=behavior_confidence,
                object_detected=object_detected,
                object_label=object_label,
                object_confidence=object_confidence
            )

            rag_guide = search_response_guide(
                object_label=object_label,
                behavior_result=behavior_result,
                action=action,
                risk_score=risk_score
            )

            if can_save_detection(best_label, camera_name):
                video_id = (
                    f"realtime-"
                    f"{camera_name}-"
                    f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-"
                    f"{uuid.uuid4().hex[:8]}"
                )

                saved_log = save_analysis_result(
                    db=db,
                    video_id=video_id,
                    user_id=current_user.id,
                    camera_name=camera_name,
                    camera_location=camera_location,
                    behavior_result=behavior_result,
                    behavior_confidence=behavior_confidence,
                    object_detected=object_detected,
                    object_label=object_label,
                    object_confidence=object_confidence,
                    risk_score=risk_score,
                    action=action
                )

                send_discord_alert(
                    object_label=object_label,
                    risk_score=risk_score,
                    camera_name=camera_name,
                    camera_location=camera_location
                )
            else:
                skipped_duplicate = True

        return {
            "success": True,
            "camera_name": camera_name,
            "camera_location": camera_location,
            "detections": detections,
            "saved": saved_log is not None,
            "skipped_duplicate": skipped_duplicate,
            "duplicate_block_seconds": DUPLICATE_BLOCK_SECONDS,
            "saved_video_id": saved_log.video_id if saved_log else None,
            "rag_guide": rag_guide
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }