from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import CCTVCamera, User
from app.routers.auth import get_current_user, get_current_admin


router = APIRouter(
    prefix="/cctv",
    tags=["CCTV"]
)


class CCTVCreateRequest(BaseModel):
    camera_name: str
    camera_location: str


class CCTVUpdateRequest(BaseModel):
    camera_name: str | None = None
    camera_location: str | None = None
    is_active: bool | None = None


@router.post("/")
def create_cctv_camera(
    request: CCTVCreateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    existing = db.query(CCTVCamera).filter(
        CCTVCamera.camera_name == request.camera_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 CCTV 이름입니다."
        )

    camera = CCTVCamera(
        camera_name=request.camera_name,
        camera_location=request.camera_location,
        is_active=True
    )

    db.add(camera)
    db.commit()
    db.refresh(camera)

    return {
        "success": True,
        "message": "CCTV 등록 성공",
        "data": {
            "id": camera.id,
            "camera_name": camera.camera_name,
            "camera_location": camera.camera_location,
            "is_active": camera.is_active,
            "created_at": camera.created_at
        }
    }


@router.get("/")
def get_cctv_cameras(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cameras = db.query(CCTVCamera).order_by(
        CCTVCamera.id.desc()
    ).all()

    return {
        "success": True,
        "count": len(cameras),
        "data": [
            {
                "id": camera.id,
                "camera_name": camera.camera_name,
                "camera_location": camera.camera_location,
                "is_active": camera.is_active,
                "created_at": camera.created_at
            }
            for camera in cameras
        ]
    }


@router.patch("/{camera_id}")
def update_cctv_camera(
    camera_id: int,
    request: CCTVUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    camera = db.query(CCTVCamera).filter(
        CCTVCamera.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="CCTV 정보를 찾을 수 없습니다."
        )

    if request.camera_name is not None:
        duplicated = db.query(CCTVCamera).filter(
            CCTVCamera.camera_name == request.camera_name,
            CCTVCamera.id != camera_id
        ).first()

        if duplicated:
            raise HTTPException(
                status_code=400,
                detail="이미 존재하는 CCTV 이름입니다."
            )

        camera.camera_name = request.camera_name

    if request.camera_location is not None:
        camera.camera_location = request.camera_location

    if request.is_active is not None:
        camera.is_active = request.is_active

    db.commit()
    db.refresh(camera)

    return {
        "success": True,
        "message": "CCTV 정보 수정 성공",
        "data": {
            "id": camera.id,
            "camera_name": camera.camera_name,
            "camera_location": camera.camera_location,
            "is_active": camera.is_active,
            "created_at": camera.created_at
        }
    }


@router.delete("/{camera_id}")
def delete_cctv_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    camera = db.query(CCTVCamera).filter(
        CCTVCamera.id == camera_id
    ).first()

    if not camera:
        raise HTTPException(
            status_code=404,
            detail="CCTV 정보를 찾을 수 없습니다."
        )

    db.delete(camera)
    db.commit()

    return {
        "success": True,
        "message": "CCTV 삭제 성공"
    }