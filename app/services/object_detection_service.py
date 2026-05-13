from pathlib import Path

import cv2


# =========================================================
# 모델 경로 설정
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "behavior" / "best.pt"


# =========================================================
# YOLO 모델 로드
# =========================================================

model = None


def get_model():
    global model

    if model is None:
        from ultralytics import YOLO

        model = YOLO(str(MODEL_PATH))
        print("YOLO model loaded")

    return model


# =========================================================
# 위험물체 클래스
# =========================================================

DANGEROUS_CLASSES = {
    "knife",
    "knuckle duster",
    "hammer",
    "tool",
    "bat"
}


# =========================================================
# confidence threshold
# =========================================================

CONF_THRESHOLD = 0.85


# =========================================================
# 위험물체 감지
# =========================================================

def detect_objects(video_path: str):
    model = get_model()

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception(f"영상 열기 실패: {video_path}")

    detected = False
    best_label = None
    best_conf = 0.0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # =================================================
        # YOLO 추론
        # =================================================

        results = model(
            frame,
            verbose=False
        )

        for r in results:

            for box in r.boxes:

                cls_id = int(box.cls[0])

                conf = float(box.conf[0])

                label = model.names[cls_id].lower()

                print(
                    f"YOLO 감지: "
                    f"{label} / "
                    f"confidence: {conf:.3f}"
                )

                # =========================================
                # 위험물체 + threshold 확인
                # =========================================

                if (
                    label in DANGEROUS_CLASSES
                    and conf >= CONF_THRESHOLD
                ):

                    if conf > best_conf:

                        detected = True
                        best_label = label
                        best_conf = conf

    cap.release()

    return (
        detected,
        best_label,
        round(best_conf, 4)
    )
