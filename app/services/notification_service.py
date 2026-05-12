import requests
from datetime import datetime


DISCORD_WEBHOOK_URL = (
    "https://discord.com/api/webhooks/"
    "1502272451654979626/"
    "l-qxZPDBBWtaq4pcF0_gsj0KE4Iu81AGXsL3gPdEMvG9e6xLlUB1GQp3mlhwa99wMino"
)


def send_discord_alert(
    object_label: str,
    risk_score: float,
    camera_name: str,
    camera_location: str
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = {
        "content": (
            "🚨 위험 감지 알림 🚨\n\n"
            f"📍 CCTV: {camera_name}\n"
            f"📌 위치: {camera_location}\n"
            f"🔪 탐지 물체: {object_label}\n"
            f"⚠ 위험도: {risk_score}\n"
            f"🕒 시간: {now}\n\n"
            "즉시 상황을 확인하세요."
        )
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=message,
            timeout=5
        )

        return response.status_code == 204

    except Exception as e:
        print(f"[Discord Alert Error] {e}")
        return False