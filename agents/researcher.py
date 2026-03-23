"""Researcher エージェント

世界中の占い手法を収集・分類し、Obsidian Vaultにノートを作成する。
anthropic SDK の tool use パターンで実装。
"""

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import list_notes, read_note, search_notes, write_note

# --- Claude に公開するツール定義 ---

TOOLS = [
    {
        "name": "vault_write_note",
        "description": "Obsidian Vaultにノートを作成または上書きする",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "Vaultルートからの相対パス (例: 10_Research/East-Asia/四柱推命.md)",
                },
                "frontmatter": {
                    "type": "object",
                    "description": "YAMLフロントマターの辞書",
                },
                "body": {
                    "type": "string",
                    "description": "Markdownの本文",
                },
            },
            "required": ["relative_path", "frontmatter", "body"],
        },
    },
    {
        "name": "vault_list_notes",
        "description": "指定フォルダ内のMarkdownファイル一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Vaultルートからの相対フォルダパス",
                },
            },
            "required": ["folder"],
        },
    },
    {
        "name": "vault_search_notes",
        "description": "ノートの内容を全文検索する（正規表現対応）",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "検索クエリ"},
                "folder": {"type": "string", "description": "検索対象フォルダ（空=全体）"},
            },
            "required": ["query"],
        },
    },
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
]

# --- ツールハンドラ ---

TOOL_HANDLERS = {
    "vault_write_note": lambda relative_path, frontmatter, body: write_note(
        relative_path, frontmatter, body
    ),
    "vault_list_notes": lambda folder: list_notes(folder),
    "vault_search_notes": lambda query, folder="": search_notes(query, folder),
    "vault_read_note": lambda relative_path: read_note(relative_path),
}


def run(target: str, existing_data: str = "") -> str:
    """Researcherエージェントを実行する。"""
    system_prompt = load_prompt("researcher")

    user_prompt = f"""以下の占い手法について調査し、Obsidian Vaultにリサーチノートを作成してください。

## 調査対象
{target}

## 既存データ
{existing_data if existing_data else "（なし）"}

## 手順
1. まず vault_list_notes で 10_Research/ 配下に既存ノートがないか確認
2. vault_search_notes で既存データに該当する情報がないか確認
3. 収集した情報を元に vault_write_note で 10_Research/{{地域}}/ 配下にノートを作成
   - frontmatterの全フィールドを埋める（占い名、地域、文化圏、入力情報、出力カテゴリ、実装難易度）
   - 科学検証ステータスは「未検証」にする
   - 概要、歴史的背景、仕組み・ロジック、実装メモのセクションを充実させる

## 重要
- 情報は正確に記述し、不確かなものには「要確認」を付ける
- 文化的・宗教的背景を尊重する
"""

    return run_agent_loop(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        tools=TOOLS,
        tool_handlers=TOOL_HANDLERS,
    )


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "四柱推命"
    print(run(target))
