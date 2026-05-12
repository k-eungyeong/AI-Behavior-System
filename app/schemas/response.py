from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    video_id: str
    behavior_result: int
    behavior_confidence: float
    object_detected: bool
    object_label: str | None = None
    object_confidence: float | None = None
    risk_score: float
    action: str
