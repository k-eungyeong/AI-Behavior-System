import os
import warnings

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

warnings.filterwarnings(
    "ignore",
    message="SymbolDatabase.GetPrototype.*"
)

warnings.filterwarnings(
    "ignore",
    category=UserWarning
)
from pathlib import Path

import cv2
import joblib
import mediapipe as mp
import numpy as np
import torch
import torch.nn as nn

from app.services.object_detection_service import detect_objects


# =========================================================
# 경로 설정
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "behavior" / "lstm_model.pth"
SCALER_PATH = BASE_DIR / "behavior" / "scaler.pkl"

SEQUENCE_LEN = 30


# =========================================================
# LSTM 모델 정의
# =========================================================

class LSTMClassifier(nn.Module):
    def __init__(self, input_size=99, hidden_size=128, num_layers=2):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3
        )

        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]).squeeze()


# =========================================================
# 디바이스 설정
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# =========================================================
# 모델 로드
# =========================================================

model = LSTMClassifier().to(device)

model.load_state_dict(
    torch.load(MODEL_PATH, map_location=device)
)

model.eval()

print("✅ LSTM 모델 로드 완료")


# =========================================================
# scaler 로드
# =========================================================

scaler = joblib.load(SCALER_PATH)

print("✅ scaler 로드 완료")


# =========================================================
# MediaPipe Pose 초기화
# =========================================================

pose = mp.solutions.pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5
)

print("✅ MediaPipe Pose 초기화 완료")


# =========================================================
# 행동 분석 모델
# =========================================================

def run_behavior_model(video_path: str):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception(f"영상 열기 실패: {video_path}")

    frame_buffer = []
    results_list = []

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        image_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = pose.process(image_rgb)

        if result.pose_landmarks:

            landmarks = []

            for lm in result.pose_landmarks.landmark:
                landmarks.extend([
                    lm.x,
                    lm.y,
                    lm.z
                ])

            frame_buffer.append(landmarks)

            # 30프레임 단위 분석
            if len(frame_buffer) == SEQUENCE_LEN:

                seq = np.array(
                    frame_buffer,
                    dtype=np.float32
                )

                # 정규화
                seq = scaler.transform(seq)

                seq_tensor = (
                    torch.tensor(
                        seq,
                        dtype=torch.float32
                    )
                    .unsqueeze(0)
                    .to(device)
                )

                with torch.no_grad():

                    prob = model(seq_tensor).item()

                    pred = 1 if prob > 0.5 else 0

                    results_list.append(
                        (pred, prob)
                    )

                frame_buffer = []

    cap.release()

    # 관절 인식 실패
    if not results_list:
        return 0, 0.0

    abnormal_count = sum(
        1
        for pred, _ in results_list
        if pred == 1
    )

    total_sequences = len(results_list)

    abnormal_ratio = (
        abnormal_count / total_sequences
    )

    avg_confidence = float(
        np.mean([
            prob
            for _, prob in results_list
        ])
    )

    final_pred = (
        1 if abnormal_ratio >= 0.3 else 0
    )

    return final_pred, avg_confidence


# =========================================================
# 전체 AI 파이프라인
# =========================================================

def run_ai_pipeline(video_path: str):

    # 1. 행동 분석
    behavior_result, behavior_confidence = (
        run_behavior_model(video_path)
    )

    # 2. YOLO 위험물체 감지
    object_detected, object_label, object_confidence = (
        detect_objects(video_path)
    )

    return {
        "behavior_result": behavior_result,
        "behavior_confidence": round(
            behavior_confidence,
            4
        ),
        "object_detected": object_detected,
        "object_label": object_label,
        "object_confidence": object_confidence
    }