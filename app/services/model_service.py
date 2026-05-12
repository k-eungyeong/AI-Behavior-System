def calculate_risk_and_action(
    behavior_result: int,
    behavior_confidence: float,
    object_detected: bool,
    object_label: str | None,
    object_confidence: float | None
) -> tuple[float, str]:

    """
    행동 분석 + 위험물체 감지 기반 위험도 계산
    """

    risk_score = 0.0

    # =====================================================
    # 1. 행동 이상 여부 반영
    # =====================================================

    if behavior_result == 1:
        risk_score += behavior_confidence * 60

    # =====================================================
    # 2. 위험물체 감지 반영
    # =====================================================

    if object_detected and object_confidence is not None:
        risk_score += object_confidence * 40

    # =====================================================
    # 3. 위험물체 종류별 가중치
    # =====================================================

    dangerous_object_weights = {

        # 칼
        "knife": 35,

        # 너클
        "knuckle duster": 30,

        # 망치
        "hammer": 25,

        # 공구류
        "tool": 15,

        # 야구방망이
        "bat": 20
    }

    if object_label is not None:

        label = object_label.lower()

        if label in dangerous_object_weights:

            risk_score += dangerous_object_weights[label]

    # =====================================================
    # 4. 최대 점수 제한
    # =====================================================

    risk_score = min(risk_score, 100.0)

    risk_score = round(risk_score, 2)

    # =====================================================
    # 5. 대응 액션 결정
    # =====================================================

    if risk_score < 30:

        action = "none"

    elif risk_score < 60:

        action = "alert"

    elif risk_score < 85:

        action = "broadcast"

    else:

        action = "report"

    return risk_score, action