from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

security = HTTPBearer()


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        (User.email == request.email) |
        (User.username == request.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 사용자입니다."
        )

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "회원가입 성공",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    if not verify_password(
        request.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="비활성화된 계정입니다."
        )

    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })

    return {
        "success": True,
        "message": "로그인 성공",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 토큰입니다."
        )

    user_id = payload.get("user_id")

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다."
        )

    return user


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }


def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="관리자 권한이 필요합니다."
        )

    return current_user

@router.post("/create-first-admin")
def create_first_admin(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    existing_admin = db.query(User).filter(
        User.role == "admin"
    ).first()

    if existing_admin:
        raise HTTPException(
            status_code=403,
            detail="이미 관리자 계정이 존재합니다."
        )

    existing_user = db.query(User).filter(
        (User.email == request.email) |
        (User.username == request.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 사용자입니다."
        )

    admin_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        role="admin"
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return {
        "success": True,
        "message": "최초 관리자 계정 생성 성공",
        "user": {
            "id": admin_user.id,
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role
        }
    }