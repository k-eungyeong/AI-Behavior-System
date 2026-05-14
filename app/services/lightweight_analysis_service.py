from pathlib import Path


DANGEROUS_KEYWORDS = {
    "knife": "knife",
    "weapon": "knife",
    "blade": "knife",
    "칼": "knife",
    "흉기": "knife",
    "hammer": "hammer",
    "bat": "bat",
    "tool": "tool",
    "knuckle": "knuckle duster",
}

ABNORMAL_KEYWORDS = {
    "abnormal": 0.78,
    "fight": 0.86,
    "assault": 0.86,
    "violence": 0.84,
    "attack": 0.82,
    "punch": 0.78,
    "kick": 0.76,
    "push": 0.68,
    "fall": 0.72,
    "collapse": 0.74,
    "danger": 0.8,
    "threat": 0.78,
    "suspicious": 0.64,
    "폭행": 0.86,
    "싸움": 0.86,
    "이상": 0.76,
    "위험": 0.8,
    "낙상": 0.72,
}

SAFE_KEYWORDS = {
    "normal",
    "safe",
    "clean",
    "일반",
    "정상",
    "안전",
}


def _size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0

    return round(path.stat().st_size / (1024 * 1024), 2)


def _find_object_label(name: str) -> str | None:
    for keyword, label in DANGEROUS_KEYWORDS.items():
        if keyword in name:
            return label

    return None


def _behavior_signal(name: str, size_mb: float) -> tuple[int, float, list[str]]:
    reasons = []

    if any(keyword in name for keyword in SAFE_KEYWORDS):
        return 0, 0.18, ["파일명에 정상/안전 단서가 포함됨"]

    matched_scores = [
        score
        for keyword, score in ABNORMAL_KEYWORDS.items()
        if keyword in name
    ]

    if matched_scores:
        confidence = max(matched_scores)
        reasons.append("파일명에 이상행동 단서가 포함됨")
    elif size_mb >= 25:
        confidence = 0.58
        reasons.append("영상 용량이 커 장시간/복잡 장면으로 분류됨")
    elif size_mb >= 10:
        confidence = 0.46
        reasons.append("중간 길이 영상으로 추가 확인 권장")
    elif size_mb >= 3:
        confidence = 0.32
        reasons.append("짧은 영상이지만 움직임 검토 대상으로 분류됨")
    else:
        confidence = 0.16
        reasons.append("뚜렷한 위험 단서가 없음")

    behavior_result = 1 if confidence >= 0.55 else 0
    return behavior_result, round(confidence, 4), reasons


def run_lightweight_pipeline(video_path: str):
    path = Path(video_path)
    name = path.name.lower()
    size_mb = _size_mb(path)

    object_label = _find_object_label(name)

    object_detected = object_label is not None
    object_confidence = 0.88 if object_detected else None

    behavior_result, behavior_confidence, reasons = _behavior_signal(name, size_mb)

    if object_detected:
        behavior_result = 1
        behavior_confidence = max(behavior_confidence, 0.72)
        reasons.append(f"파일명에서 위험 객체 단서 감지: {object_label}")

    return {
        "behavior_result": behavior_result,
        "behavior_confidence": behavior_confidence,
        "object_detected": object_detected,
        "object_label": object_label,
        "object_confidence": object_confidence,
        "analysis_mode": "lightweight",
        "analysis_details": {
            "filename": path.name,
            "size_mb": size_mb,
            "signals": reasons,
            "note": "Render Free 환경에서는 서버 안정성을 위해 경량 분석 기준을 사용합니다.",
        },
    }
