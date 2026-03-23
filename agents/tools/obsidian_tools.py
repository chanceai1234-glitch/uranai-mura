"""Obsidian Vault 操作を Agent SDK のカスタムツールとして定義する。

各関数は Agent SDK の tool として登録され、エージェントから呼び出される。
"""

from claude_agent_sdk import tool

from agents.tools.obsidian import (
    append_to_note,
    get_note_status,
    list_notes,
    read_note,
    search_notes,
    write_note,
)


@tool(
    "vault_read_note",
    "Obsidian Vaultからノートを読み取る。frontmatterとbodyを返す。",
    {"relative_path": str},
)
async def vault_read_note(args: dict) -> dict:
    try:
        result = read_note(args["relative_path"])
        import json

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2),
                }
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool(
    "vault_write_note",
    "Obsidian Vaultにノートを作成または上書きする。",
    {"relative_path": str, "frontmatter": dict, "body": str},
)
async def vault_write_note(args: dict) -> dict:
    try:
        path = write_note(args["relative_path"], args["frontmatter"], args["body"])
        return {"content": [{"type": "text", "text": f"Written: {path}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool(
    "vault_append_to_note",
    "既存ノートの指定セクションにテキストを追記する。",
    {"relative_path": str, "section": str, "text": str},
)
async def vault_append_to_note(args: dict) -> dict:
    try:
        path = append_to_note(args["relative_path"], args["section"], args["text"])
        return {"content": [{"type": "text", "text": f"Appended to: {path}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool(
    "vault_list_notes",
    "指定フォルダ内のMarkdownファイル一覧を返す。",
    {"folder": str, "recursive": bool},
)
async def vault_list_notes(args: dict) -> dict:
    try:
        notes = list_notes(args["folder"], args.get("recursive", True))
        import json

        return {
            "content": [
                {"type": "text", "text": json.dumps(notes, ensure_ascii=False, indent=2)}
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool(
    "vault_search_notes",
    "ノートの内容を全文検索する（正規表現対応）。",
    {"query": str, "folder": str},
)
async def vault_search_notes(args: dict) -> dict:
    try:
        results = search_notes(args["query"], args.get("folder", ""))
        import json

        return {
            "content": [
                {"type": "text", "text": json.dumps(results, ensure_ascii=False, indent=2)}
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool(
    "vault_get_note_status",
    "ノートのfrontmatterからステータス情報を取得する。",
    {"relative_path": str},
)
async def vault_get_note_status(args: dict) -> dict:
    try:
        status = get_note_status(args["relative_path"])
        import json

        return {
            "content": [
                {"type": "text", "text": json.dumps(status, ensure_ascii=False, indent=2)}
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


# ツール一覧（MCP サーバー登録用）
ALL_VAULT_TOOLS = [
    vault_read_note,
    vault_write_note,
    vault_append_to_note,
    vault_list_notes,
    vault_search_notes,
    vault_get_note_status,
]
