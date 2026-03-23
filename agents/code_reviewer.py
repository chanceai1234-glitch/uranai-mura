"""Code Reviewer エージェント

Implementer・Testerのコードを品質チェックし、承認または差し戻しを判定する。
"""

import json
import os
from pathlib import Path

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import read_note

SRC_DIR = Path(os.environ.get("SRC_DIR", "/app/src"))
TESTS_DIR = Path(os.environ.get("TESTS_DIR", "/app/tests"))

# レビュー結果を格納する
_review_result: dict | None = None


def _read_file(relative_path: str, base: str = "src") -> str:
    base_dir = SRC_DIR if base == "src" else TESTS_DIR
    file_path = base_dir / relative_path
    if not file_path.exists():
        return f"Error: File not found: {file_path}"
    return file_path.read_text(encoding="utf-8")


def _list_files(folder: str = "", base: str = "src") -> list[str]:
    base_dir = SRC_DIR if base == "src" else TESTS_DIR
    search_path = base_dir / folder if folder else base_dir
    if not search_path.exists():
        return []
    return [str(p.relative_to(base_dir)) for p in search_path.rglob("*.py")]


def _handle_submit_review(approved: bool, feedback: str, issues: list[str]) -> str:
    global _review_result
    _review_result = {"approved": approved, "feedback": feedback, "issues": issues}
    return json.dumps(_review_result, ensure_ascii=False)


TOOLS = [
    {
        "name": "vault_read_note",
        "description": "Obsidian Vaultからノート（設計書等）を読み取る",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "ノートの相対パス"},
            },
            "required": ["relative_path"],
        },
    },
    {
        "name": "read_source",
        "description": "src/配下のソースコードを読み取る",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "src/からの相対パス"},
            },
            "required": ["relative_path"],
        },
    },
    {
        "name": "read_test",
        "description": "tests/配下のテストコードを読み取る",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "tests/からの相対パス"},
            },
            "required": ["relative_path"],
        },
    },
    {
        "name": "list_source_files",
        "description": "src/配下のファイル一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "サブフォルダ"},
            },
            "required": [],
        },
    },
    {
        "name": "list_test_files",
        "description": "tests/配下のファイル一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "サブフォルダ"},
            },
            "required": [],
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
                    "description": "問題点のリスト（重大度順）",
                },
            },
            "required": ["approved", "feedback", "issues"],
        },
    },
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "read_source": lambda relative_path: _read_file(relative_path, "src"),
    "read_test": lambda relative_path: _read_file(relative_path, "tests"),
    "list_source_files": lambda folder="": _list_files(folder, "src"),
    "list_test_files": lambda folder="": _list_files(folder, "tests"),
    "submit_review": _handle_submit_review,
}


def run(uranai_name: str, architecture_path: str = "") -> dict:
    """Code Reviewerを実行する。"""
    global _review_result
    _review_result = None

    system_prompt = load_prompt("code_reviewer")
    arch_path = architecture_path or f"40_Platform/Architecture/{uranai_name}.md"

    user_prompt = f"""以下の占いロジックの実装コードとテストコードをレビューしてください。

## 対象
{uranai_name}

## 設計書
{arch_path}

## 手順
1. vault_read_note で設計書を読む
2. list_source_files と list_test_files でファイル一覧を確認
3. read_source / read_test で全コードを読む
4. 以下のチェックリストに基づいてレビュー
5. submit_review でレビュー結果を提出

## チェックリスト

### 必須（ブロッカー）
- [ ] セキュリティ脆弱性がないか（入力バリデーション、インジェクション対策）
- [ ] 設計書の仕様に準拠しているか
- [ ] テストが受け入れ条件をカバーしているか
- [ ] 型ヒントが付いているか

### 重要
- [ ] エラーハンドリングが適切か
- [ ] コードの重複がないか
- [ ] 関数が単一責任を守っているか
- [ ] マスタデータとロジックが適切に分離されているか

### 推奨（nit）
- [ ] 変数名・関数名が適切か
- [ ] docstringが有用か
- [ ] コードの構造が読みやすいか
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
    uranai = sys.argv[1] if len(sys.argv) > 1 else "四柱推命"
    result = run(uranai)
    print(json.dumps(result, ensure_ascii=False, indent=2))
