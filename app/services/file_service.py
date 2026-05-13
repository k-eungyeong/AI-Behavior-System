import os

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def get_uploaded_file_path(video_id: str) -> str | None:
    """
    uploads 폴더에서 video_id로 시작하는 파일을 찾아 경로를 반환한다.
    없으면 None 반환.
    """
    if not os.path.exists(UPLOAD_DIR):
        return None

    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(video_id + "_"):
            return os.path.join(UPLOAD_DIR, filename)

    return None