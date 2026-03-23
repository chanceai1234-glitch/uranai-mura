"""Phase 3 パイプライン: Requirements → Architect → Implementer → Tester → Code Reviewer

1つの占い手法の体験機能について、要件定義→設計→実装→テスト→レビューの
一連のフローを実行する。
"""

import json
import sys
from datetime import datetime

from agents.requirements_analyst import run as run_requirements
from agents.architect import run as run_architect
from agents.implementer import run as run_implementer
from agents.tester import run as run_tester
from agents.code_reviewer import run as run_code_reviewer


def run_pipeline(
    uranai_name: str,
    research_note_path: str = "",
    max_review_retries: int = 2,
) -> dict:
    """Phase 3 パイプラインを実行する。"""
    requirement_path = f"40_Platform/Requirements/{uranai_name}.md"
    architecture_path = f"40_Platform/Architecture/{uranai_name}.md"
    timestamp = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"Phase 3 Pipeline: {uranai_name}")
    print(f"{'='*60}")

    # Step 1: Requirements Analyst
    print(f"\n[1/5] Requirements Analyst: 要件定義中...")
    run_requirements(uranai_name, research_note_path)
    print(f"  → 要件定義書作成完了: {requirement_path}")

    # Step 2: Architect
    print(f"\n[2/5] Architect: 設計中...")
    run_architect(uranai_name, requirement_path)
    print(f"  → 設計書作成完了: {architecture_path}")

    # Step 3-5: Implementer → Tester → Code Reviewer（リトライあり）
    code_review = None
    for attempt in range(max_review_retries + 1):
        # Step 3: Implementer
        print(f"\n[3/5] Implementer: 実装中... (試行 {attempt + 1})")
        run_implementer(uranai_name, architecture_path)
        print(f"  → 実装完了")

        # Step 4: Tester
        print(f"\n[4/5] Tester: テスト実行中...")
        test_result = run_tester(uranai_name, requirement_path)
        print(f"  → テスト完了")

        # Step 5: Code Reviewer
        print(f"\n[5/5] Code Reviewer: レビュー中...")
        code_review = run_code_reviewer(uranai_name, architecture_path)
        print(f"  → コードレビュー: {'承認' if code_review['approved'] else '差し戻し'}")

        if code_review["approved"]:
            print(f"\n✅ {uranai_name}: コードレビュー承認")
            return {
                "uranai_name": uranai_name,
                "requirement": requirement_path,
                "architecture": architecture_path,
                "code_review": code_review,
                "status": "completed",
                "timestamp": timestamp,
            }

        if attempt < max_review_retries:
            print(f"  → 差し戻し理由: {code_review.get('feedback', '')[:100]}")
            print("  → 再実装...")

    print(f"\n⚠️ {uranai_name}: コードレビュー未承認のまま上限到達")
    return {
        "uranai_name": uranai_name,
        "requirement": requirement_path,
        "architecture": architecture_path,
        "code_review": code_review,
        "status": "review_failed",
        "timestamp": timestamp,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agents.pipeline_phase3 <占い名> [リサーチノートパス]")
        sys.exit(1)

    uranai_name = sys.argv[1]
    research = sys.argv[2] if len(sys.argv) > 2 else ""
    result = run_pipeline(uranai_name, research)
    print(f"\n{'='*60}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
