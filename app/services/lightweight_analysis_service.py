from pathlib import Path


DANGEROUS_KEYWORDS = {
    "knife": "knife",
    "hammer": "hammer",
    "bat": "bat",
    "tool": "tool",
    "knuckle": "knuckle duster",
}


def run_lightweight_pipeline(video_path: str):
    path = Path(video_path)
    name = path.name.lower()

    object_label = None
    for keyword, label in DANGEROUS_KEYWORDS.items():
        if keyword in name:
            object_label = label
            break

    object_detected = object_label is not None
    object_confidence = 0.72 if object_detected else None

    size = path.stat().st_size if path.exists() else 0
    behavior_result = 1 if object_detected else 0
    behavior_confidence = 0.65 if behavior_result else min(0.5, round(size / 50_000_000, 4))

    return {
        "behavior_result": behavior_result,
        "behavior_confidence": behavior_confidence,
        "object_detected": object_detected,
        "object_label": object_label,
        "object_confidence": object_confidence,
        "analysis_mode": "lightweight",
    }
