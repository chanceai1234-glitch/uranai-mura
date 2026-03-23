"""Requirements Analyst エージェント

リサーチ結果と実装ロジック仕様をエンジニアリング要件に変換する。
"""

import json

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import list_notes, read_note, search_notes, write_note
from agents.tools.github import create_issue

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
        "name": "vault_write_note",
        "description": "Obsidian Vaultにノートを作成または上書きする",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "相対パス"},
                "frontmatter": {"type": "object", "description": "フロントマター"},
                "body": {"type": "string", "description": "本文"},
            },
            "required": ["relative_path", "frontmatter", "body"],
        },
    },
    {
        "name": "vault_list_notes",
        "description": "指定フォルダ内のノート一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "フォルダパス"},
            },
            "required": ["folder"],
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
        "name": "github_create_issue",
        "description": "GitHub Issueを作成する",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Issueタイトル"},
                "body": {"type": "string", "description": "Issue本文（Markdown）"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "ラベルのリスト",
                },
            },
            "required": ["title", "body"],
        },
    },
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "vault_write_note": lambda relative_path, frontmatter, body: write_note(
        relative_path, frontmatter, body
    ),
    "vault_list_notes": lambda folder: list_notes(folder),
    "vault_search_notes": lambda query, folder="": search_notes(query, folder),
    "github_create_issue": lambda title, body, labels=None: create_issue(
        title, body, labels or []
    ),
}


def run(uranai_name: str, research_note_path: str = "", logic_data: str = "") -> str:
    """Requirements Analystを実行する。"""
    system_prompt = load_prompt("requirements_analyst")

    user_prompt = f"""以下の占い手法の体験機能について要件定義を行ってください。

## 対象占い
{uranai_name}

## 参照ノート
{f"- リサーチノート: {research_note_path}" if research_note_path else ""}

## 既存の実装ロジック情報
{logic_data if logic_data else "（vault内のリサーチノートを参照してください）"}

## 手順
1. vault_read_note でリサーチノートを読み、占いの仕組みを理解する
2. ユーザーストーリー・受け入れ条件・入出力仕様を定義する
3. vault_write_note で 40_Platform/Requirements/{uranai_name}.md に要件定義書を保存
4. github_create_issue で対応するGitHub Issueを作成（ラベル: feature, platform）

## 要件定義のフォーマット（frontmatter）
- 機能名: "{uranai_name}体験機能"
- 対象占い: ["{uranai_name}"]
- 優先度: "中"
- ステータス: "未着手"
- tags: [要件, platform, {uranai_name}]

## 要件に含めるべき内容
1. ユーザーストーリー（誰が、何をしたい、なぜ）
2. 機能概要
3. 受け入れ条件（チェックリスト形式）
4. 入力仕様（パラメータ、型、必須/任意）
5. 出力仕様（レスポンス形式）
6. 非機能要件
   - パフォーマンス: レスポンスタイム目標
   - セキュリティ: 入力バリデーション
   - アクセシビリティ: WCAG 2.1 AA準拠
   - 多言語: 日本語基本、英語対応視野

## 重要
- 新規調査はしない。既存データを元にエンジニアリング要件に変換する
- 受け入れ条件は検証可能な形で記述する
- 占い結果画面には必ず「科学的検証の結果」へのリンクを含める要件を入れる
"""

    return run_agent_loop(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        tools=TOOLS,
        tool_handlers=TOOL_HANDLERS,
    )


if __name__ == "__main__":
    import sys
    uranai = sys.argv[1] if len(sys.argv) > 1 else "四柱推命"
    research = sys.argv[2] if len(sys.argv) > 2 else f"10_Research/East-Asia/{uranai}.md"
    print(run(uranai, research))
