import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
MANUAL_PATH = BASE_DIR / "rag" / "response_manual.json"


def load_response_manual():
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def search_response_guide(
    object_label: str | None = None,
    behavior_result: int | str | None = None,
    action: str | None = None,
    risk_score: float | None = None
):
    manual = load_response_manual()

    query_terms = []

    if object_label:
        query_terms.append(str(object_label).lower())

    if behavior_result == 1 or behavior_result == "abnormal":
        query_terms.append("abnormal")

    if action:
        query_terms.append(str(action).lower())

    if risk_score is not None:
        if risk_score >= 85:
            query_terms.append("report")
        elif risk_score >= 60:
            query_terms.append("broadcast")
        elif risk_score >= 30:
            query_terms.append("alert")
        else:
            query_terms.append("safe")

    best_item = None
    best_score = 0

    for item in manual:
        score = 0

        keywords = [
            keyword.lower()
            for keyword in item.get("keywords", [])
        ]

        for term in query_terms:
            if term in keywords:
                score += 1

        if score > best_score:
            best_score = score
            best_item = item

    if best_item is None:
        best_item = next(
            (
                item for item in manual
                if "normal" in [
                    keyword.lower()
                    for keyword in item.get("keywords", [])
                ]
            ),
            None
        )

    return {
        "matched": best_item is not None,
        "score": best_score,
        "query_terms": query_terms,
        "guide": best_item
    }