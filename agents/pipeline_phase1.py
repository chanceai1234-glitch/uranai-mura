"""Phase 1 パイプライン: Researcher → Scientist → Research Reviewer

1つの占い手法に対して、リサーチ→科学検証→レビューの一連のフローを実行する。
"""

import asyncio
import sys
from datetime import datetime

from agents.researcher import run as run_researcher
from agents.scientist import run as run_scientist
from agents.research_reviewer import run as run_reviewer


async def run_pipeline(
    uranai_name: str,
    region: str = "East-Asia",
    existing_data: str = "",
    max_review_retries: int = 2,
) -> dict:
    """Phase 1 パイプラインを実行する。

    Args:
        uranai_name: 占い名（例: "四柱推命"）
        region: 地域名（例: "East-Asia"）
        existing_data: 既存のリサーチデータ
        max_review_retries: レビュー差し戻し時の最大リトライ回数

    Returns:
        {
            "uranai_name": str,
            "research_note": str,
            "science_note": str,
            "review_result": dict,
            "status": "completed" | "review_failed",
            "timestamp": str,
        }
    """
    research_note_path = f"10_Research/{region}/{uranai_name}.md"
    science_note_path = f"20_Science/Verdicts/{uranai_name}.md"
    timestamp = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"Phase 1 Pipeline: {uranai_name}")
    print(f"{'='*60}")

    # Step 1: Researcher
    print(f"\n[1/3] Researcher: {uranai_name} を調査中...")
    research_result = await run_researcher(uranai_name, existing_data)
    print(f"  → リサーチノート作成完了: {research_note_path}")

    # Step 2: Scientist
    print(f"\n[2/3] Scientist: 科学的検証を実施中...")
    science_result = await run_scientist(uranai_name, research_note_path)
    print(f"  → 検証ノート作成完了: {science_note_path}")

    # Step 3: Research Reviewer（リトライあり）
    for attempt in range(max_review_retries + 1):
        print(f"\n[3/3] Research Reviewer: レビュー中... (試行 {attempt + 1})")

        # リサーチノートのレビュー
        research_review = await run_reviewer(research_note_path, "research")
        print(f"  → リサーチレビュー: {'承認' if research_review['approved'] else '差し戻し'}")

        # 科学検証ノートのレビュー
        science_review = await run_reviewer(science_note_path, "science")
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
                research_result = await run_researcher(
                    uranai_name,
                    f"前回のレビューフィードバック: {feedback}\n\n{existing_data}",
                )
            if not science_review["approved"]:
                science_result = await run_scientist(uranai_name, research_note_path)

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


async def run_batch_pipeline(
    targets: list[dict],
    max_concurrent: int = 3,
) -> list[dict]:
    """複数の占い手法に対してパイプラインを並列実行する。

    Args:
        targets: [{"name": "四柱推命", "region": "East-Asia"}, ...]
        max_concurrent: 最大並列数

    Returns:
        各パイプラインの結果リスト
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _run_with_semaphore(target: dict) -> dict:
        async with semaphore:
            return await run_pipeline(
                uranai_name=target["name"],
                region=target.get("region", "East-Asia"),
                existing_data=target.get("existing_data", ""),
            )

    tasks = [_run_with_semaphore(t) for t in targets]
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agents.pipeline_phase1 <占い名> [地域]")
        print("Example: python -m agents.pipeline_phase1 四柱推命 East-Asia")
        sys.exit(1)

    uranai_name = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "East-Asia"

    result = asyncio.run(run_pipeline(uranai_name, region))
    print(f"\n{'='*60}")
    print(f"結果: {result['status']}")
    print(f"リサーチノート: {result['research_note']}")
    print(f"科学検証ノート: {result['science_note']}")
