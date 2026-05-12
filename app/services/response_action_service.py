def execute_response_action(action: str, video_id: str, risk_score: float) -> str:
    """
    위험도에 따라 대응 액션을 시뮬레이션한다.
    실제 서비스에서는 이 부분이 알림 전송, 방송 시스템, 신고 API 등과 연결될 수 있다.
    """

    if action == "alert":
        return (
            f"[ALERT] 관리자에게 알림을 전송했습니다. "
            f"video_id={video_id}, risk_score={risk_score}"
        )

    if action == "broadcast":
        return (
            f"[BROADCAST] 주변 경고 방송을 실행했습니다. "
            f"video_id={video_id}, risk_score={risk_score}"
        )

    if action == "report":
        return (
            f"[REPORT] 긴급 신고 시뮬레이션을 실행했습니다. "
            f"video_id={video_id}, risk_score={risk_score}"
        )

    return (
        f"[NONE] 추가 대응이 필요하지 않습니다. "
        f"video_id={video_id}, risk_score={risk_score}"
    )