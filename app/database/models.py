from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    
class CCTVCamera(Base):
    __tablename__ = "cctv_cameras"

    id = Column(Integer, primary_key=True, index=True)

    camera_name = Column(String, unique=True, index=True, nullable=False)
    camera_location = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)

    video_id = Column(String, unique=True, index=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    camera_name = Column(String, nullable=True)
    camera_location = Column(String, nullable=True)

    behavior_result = Column(Integer, nullable=False)
    behavior_confidence = Column(Float, nullable=False)

    object_detected = Column(Boolean, nullable=False)
    object_label = Column(String, nullable=True)
    object_confidence = Column(Float, nullable=True)

    risk_score = Column(Float, nullable=False)
    action = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)