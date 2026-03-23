"""Orchestrator エージェント

全エージェントのタスク割り当て・進捗管理・依存関係解決を行う。
GitHub IssueをトリガーにしてパイプラインをIssueラベルに応じて振り分ける。
"""

import json
import sys
from datetime import datetime

from agents.tools.obsidian import append_to_note, read_note


def dispatch(issue: dict) -> dict:
    """GitHub Issueの内容を解析し、適切なパイプラインを実行する。

    Args:
        issue: {"title": str, "body": str, "labels": list[str], "number": int}

    Returns:
        実行結果の辞書
    """
    labels = [l.lower() for l in issue.get("labels", [])]
    title = issue.get("title", "")
    body = issue.get("body", "")
    number = issue.get("number", 0)
    timestamp = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"Orchestrator: Issue #{number} を処理中")
    print(f"Title: {title}")
    print(f"Labels: {labels}")
    print(f"{'='*60}")

    # 占い名を抽出（タイトルまたはbodyから）
    uranai_name = _extract_uranai_name(title, body)
    region = _extract_region(body)

    if not uranai_name:
        return {
            "status": "error",
            "message": "占い名を特定できませんでした。Issueのタイトルまたは本文に占い名を記載してください。",
            "timestamp": timestamp,
        }

    # ラベルに基づいてパイプラインを選択
    if "research" in labels:
        return _run_research_pipeline(uranai_name, region, number, timestamp)
    elif "content" in labels:
        return _run_content_pipeline(uranai_name, number, timestamp)
    elif "feature" in labels or "platform" in labels:
        return _run_dev_pipeline(uranai_name, number, timestamp)
    elif "full" in labels:
        return _run_full_pipeline(uranai_name, region, number, timestamp)
    else:
        # ラベルなし → research をデフォルトとする
        print("  ラベル未指定のため research パイプラインを実行します")
        return _run_research_pipeline(uranai_name, region, number, timestamp)


def _extract_uranai_name(title: str, body: str) -> str:
    """IssueのタイトルまたはBodyから占い名を抽出する。"""
    # "【占い名】" パターン
    import re
    match = re.search(r"[【\[](.+?)[】\]]", title)
    if match:
        return match.group(1)

    # タイトルそのものが占い名の場合
    if len(title) < 20 and not any(c in title for c in ".:,;!?"):
        return title.strip()

    # bodyから "占い名:" パターン
    match = re.search(r"占い名[：:]?\s*(.+?)[\n\r]", body)
    if match:
        return match.group(1).strip()

    return ""


def _extract_region(body: str) -> str:
    """Bodyから地域を抽出する。"""
    import re
    match = re.search(r"地域[：:]?\s*(.+?)[\n\r]", body)
    if match:
        region = match.group(1).strip()
        region_map = {
            "東アジア": "East-Asia", "南アジア": "South-Asia",
            "東南アジア": "Southeast-Asia", "中央アジア": "Central-Asia",
            "中東": "Middle-East", "ヨーロッパ": "Europe",
            "アフリカ": "Africa", "アメリカ": "Americas",
            "オセアニア": "Oceania", "現代": "Modern-Digital",
        }
        return region_map.get(region, region)
    return "East-Asia"


def _run_research_pipeline(uranai_name: str, region: str, issue_num: int, timestamp: str) -> dict:
    """リサーチ系パイプライン: Researcher → Scientist → Research Reviewer"""
    from agents.pipeline_phase1 import run_pipeline
    result = run_pipeline(uranai_name, region)
    result["issue_number"] = issue_num
    result["pipeline"] = "research"
    _log_to_dashboard(uranai_name, "research", result["status"], timestamp)
    return result


def _run_content_pipeline(uranai_name: str, issue_num: int, timestamp: str) -> dict:
    """コンテンツ系パイプライン: Writer → Research Reviewer"""
    from agents.writer import run as run_writer
    from agents.research_reviewer import run as run_reviewer

    science_path = f"20_Science/Verdicts/{uranai_name}.md"
    research_path = f"10_Research/East-Asia/{uranai_name}.md"

    print(f"\n[1/2] Writer: 記事作成中...")
    run_writer(uranai_name, science_path, research_path)
    draft_path = f"30_Content/Drafts/{uranai_name}.md"
    print(f"  → 記事ドラフト作成完了: {draft_path}")

    print(f"\n[2/2] Research Reviewer: 記事レビュー中...")
    review = run_reviewer(draft_path, "article")
    print(f"  → 記事レビュー: {'承認' if review['approved'] else '差し戻し'}")

    result = {
        "uranai_name": uranai_name,
        "article_draft": draft_path,
        "review": review,
        "status": "completed" if review["approved"] else "review_failed",
        "pipeline": "content",
        "issue_number": issue_num,
        "timestamp": timestamp,
    }
    _log_to_dashboard(uranai_name, "content", result["status"], timestamp)
    return result


def _run_dev_pipeline(uranai_name: str, issue_num: int, timestamp: str) -> dict:
    """開発系パイプライン: Requirements → Architect → Implementer → Tester → Code Reviewer"""
    from agents.pipeline_phase3 import run_pipeline
    research_path = f"10_Research/East-Asia/{uranai_name}.md"
    result = run_pipeline(uranai_name, research_path)
    result["issue_number"] = issue_num
    result["pipeline"] = "development"
    _log_to_dashboard(uranai_name, "development", result["status"], timestamp)
    return result


def _run_full_pipeline(uranai_name: str, region: str, issue_num: int, timestamp: str) -> dict:
    """フルパイプライン: Phase 1 → Phase 2(Writer) → Phase 3(開発)"""
    print("\n=== Phase 1: リサーチ & 科学検証 ===")
    research_result = _run_research_pipeline(uranai_name, region, issue_num, timestamp)

    if research_result["status"] != "completed":
        research_result["pipeline"] = "full (stopped at research)"
        return research_result

    print("\n=== Phase 2: コンテンツ作成 ===")
    content_result = _run_content_pipeline(uranai_name, issue_num, timestamp)

    print("\n=== Phase 3: プラットフォーム開発 ===")
    dev_result = _run_dev_pipeline(uranai_name, issue_num, timestamp)

    return {
        "uranai_name": uranai_name,
        "research": research_result,
        "content": content_result,
        "development": dev_result,
        "status": "completed",
        "pipeline": "full",
        "issue_number": issue_num,
        "timestamp": timestamp,
    }


def _log_to_dashboard(uranai_name: str, pipeline: str, status: str, timestamp: str):
    """Obsidian のダッシュボードに実行ログを追記する。"""
    try:
        log_entry = f"- **{timestamp}** | {uranai_name} | {pipeline} | {status}"
        append_to_note("99_Meta/Agent-Log.md", "## ログ", log_entry)
    except Exception:
        pass  # ダッシュボード更新失敗は無視


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agents.orchestrator '<json_issue>'")
        print('Example: python -m agents.orchestrator \'{"title":"四柱推命","labels":["research"],"number":1}\'')
        sys.exit(1)

    issue = json.loads(sys.argv[1])
    result = dispatch(issue)
    print(json.dumps(result, ensure_ascii=False, indent=2))
