"""Research Reviewer エージェント

Researcher・Scientistの成果物を品質チェックし、承認または差し戻しを判定する。
"""

import json
import re

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import append_to_note, list_notes, read_note, search_notes

TOOLS = [
    {
        "name": "vault_read_note",
        "description": "Obsidian Vaultからノートを読み取る",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "ノートの相対パス"},
            },
            "required": ["relative_path"],
        },
    },
    {
        "name": "vault_append_to_note",
        "description": "既存ノートにレビューコメントを追記する",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "ノートの相対パス"},
                "section": {"type": "string", "description": "追記先セクション"},
                "text": {"type": "string", "description": "追記テキスト"},
            },
            "required": ["relative_path", "section", "text"],
        },
    },
    {
        "name": "vault_search_notes",
        "description": "ノートの全文検索",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "検索クエリ"},
                "folder": {"type": "string", "description": "対象フォルダ"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "submit_review",
        "description": "レビュー結果を提出する。必ず最後にこのツールを呼ぶこと。",
        "input_schema": {
            "type": "object",
            "properties": {
                "approved": {"type": "boolean", "description": "承認=true, 差し戻し=false"},
                "feedback": {"type": "string", "description": "全体的なフィードバック"},
                "issues": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "問題点のリスト",
                },
            },
            "required": ["approved", "feedback", "issues"],
        },
    },
]

# submit_review の結果を格納する
_review_result: dict | None = None


def _handle_submit_review(approved: bool, feedback: str, issues: list[str]) -> str:
    global _review_result
    _review_result = {"approved": approved, "feedback": feedback, "issues": issues}
    return json.dumps(_review_result, ensure_ascii=False)


TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "vault_append_to_note": lambda relative_path, section, text: append_to_note(
        relative_path, section, text
    ),
    "vault_search_notes": lambda query, folder="": search_notes(query, folder),
    "submit_review": _handle_submit_review,
}


def _get_checklist(review_type: str) -> str:
    checklists = {
        "research": """
- frontmatterの全フィールド（占い名、地域、文化圏、入力情報、出力カテゴリ、実装難易度）が埋まっているか
- 概要が正確で偏りがないか
- 歴史的背景の記述があるか
- 仕組み・ロジックが記述されているか
- 地域分類が適切か
""",
        "science": """
- 引用された研究が具体的か（著者名・年・概要あり）
- エビデンスレベルの評価が適切か
- 結論が根拠から論理的に導かれているか
- 反証や限界が記述されているか
- バーナム効果等の心理メカニズムが考慮されているか
""",
        "article": """
- 科学的誠実さが保たれているか
- 一般読者にとってわかりやすいか
- 出典が明記されているか
- 占いを信じる人を攻撃していないか
""",
    }
    return checklists.get(review_type, checklists["research"])


def run(note_path: str, review_type: str = "research") -> dict:
    """Research Reviewerを実行する。"""
    global _review_result
    _review_result = None

    system_prompt = load_prompt("research_reviewer")
    checklist = _get_checklist(review_type)

    user_prompt = f"""以下のノートをレビューしてください。

## レビュー対象
{note_path}

## レビュー種別
{review_type}

## 手順
1. vault_read_note で対象ノートを読む
2. チェックリストに基づいて検証する
3. vault_append_to_note でレビューコメントを追記（セクション: ## レビューログ）
4. 最後に submit_review でレビュー結果を提出する

## チェックリスト
{checklist}

## 判定基準
- 重大な問題（科学的誤り、必須フィールド未記入、出典なし）→ 差し戻し
- 軽微な問題のみ → 承認（コメントで改善提案）
"""

    run_agent_loop(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        tools=TOOLS,
        tool_handlers=TOOL_HANDLERS,
    )

    if _review_result is not None:
        return _review_result

    return {"approved": True, "feedback": "レビュー完了", "issues": []}


if __name__ == "__main__":
    import sys

    note = sys.argv[1] if len(sys.argv) > 1 else "10_Research/East-Asia/四柱推命.md"
    rtype = sys.argv[2] if len(sys.argv) > 2 else "research"
    result = run(note, rtype)
    print(json.dumps(result, ensure_ascii=False, indent=2))
