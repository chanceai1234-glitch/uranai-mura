"""Phase 1 パイプライン: Researcher → Scientist → Research Reviewer

1つの占い手法に対して、リサーチ→科学検証→レビューの一連のフローを実行する。
"""

import json
import sys
from datetime import datetime

from agents.researcher import run as run_researcher
from agents.scientist import run as run_scientist
from agents.research_reviewer import run as run_reviewer


def run_pipeline(
    uranai_name: str,
    region: str = "East-Asia",
    existing_data: str = "",
    max_review_retries: int = 2,
) -> dict:
    """Phase 1 パイプラインを実行する。"""
    research_note_path = f"10_Research/{region}/{uranai_name}.md"
    science_note_path = f"20_Science/Verdicts/{uranai_name}.md"
    timestamp = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"Phase 1 Pipeline: {uranai_name}")
    print(f"{'='*60}")

    # Step 1: Researcher
    print(f"\n[1/3] Researcher: {uranai_name} を調査中...")
    research_result = run_researcher(uranai_name, existing_data)
    print(f"  → リサーチノート作成完了: {research_note_path}")

    # Step 2: Scientist
    print(f"\n[2/3] Scientist: 科学的検証を実施中...")
    science_result = run_scientist(uranai_name, research_note_path)
    print(f"  → 検証ノート作成完了: {science_note_path}")

    # Step 3: Research Reviewer（リトライあり）
    research_review = None
    science_review = None

    for attempt in range(max_review_retries + 1):
        print(f"\n[3/3] Research Reviewer: レビュー中... (試行 {attempt + 1})")

        research_review = run_reviewer(research_note_path, "research")
        print(f"  → リサーチレビュー: {'承認' if research_review['approved'] else '差し戻し'}")

        science_review = run_reviewer(science_note_path, "science")
        print(f"  → 科学検証レビュー: {'承認' if science_review['approved'] else '差し戻し'}")

        if research_review["approved"] and science_review["approved"]:
            print(f"\n✅ {uranai_name}: 全レビュー承認")
            return {
                "uranai_name": uranai_name,
                "research_note": research_note_path,
                "science_note": science_note_path,
                "review_result": {
                    "research": research_review,
                    "science": science_review,
                },
                "status": "completed",
                "timestamp": timestamp,
            }

        if attempt < max_review_retries:
            print("  → 差し戻しのため再調査...")
            if not research_review["approved"]:
                feedback = research_review.get("feedback", "")
                run_researcher(uranai_name, f"前回レビューの指摘: {feedback}")
            if not science_review["approved"]:
                run_scientist(uranai_name, research_note_path)

    print(f"\n⚠️ {uranai_name}: レビュー未承認のまま上限到達")
    return {
        "uranai_name": uranai_name,
        "research_note": research_note_path,
        "science_note": science_note_path,
        "review_result": {
            "research": research_review,
            "science": science_review,
        },
        "status": "review_failed",
        "timestamp": timestamp,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agents.pipeline_phase1 <占い名> [地域]")
        sys.exit(1)

    uranai_name = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "East-Asia"

    result = run_pipeline(uranai_name, region)
    print(f"\n{'='*60}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
