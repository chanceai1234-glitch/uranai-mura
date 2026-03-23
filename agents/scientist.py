"""Scientist エージェント

各占い手法の科学的検証を行い、エビデンスに基づいて効果を評価する。
"""

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import (
    append_to_note,
    get_note_status,
    list_notes,
    read_note,
    write_note,
)

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
        "name": "vault_append_to_note",
        "description": "既存ノートの指定セクションにテキストを追記する",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "ノートの相対パス"},
                "section": {"type": "string", "description": "追記先セクション見出し (例: ## 科学的検証)"},
                "text": {"type": "string", "description": "追記するテキスト"},
            },
            "required": ["relative_path", "section", "text"],
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
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "vault_write_note": lambda relative_path, frontmatter, body: write_note(
        relative_path, frontmatter, body
    ),
    "vault_append_to_note": lambda relative_path, section, text: append_to_note(
        relative_path, section, text
    ),
    "vault_list_notes": lambda folder: list_notes(folder),
}


def run(uranai_name: str, research_note_path: str) -> str:
    """Scientistエージェントを実行する。"""
    system_prompt = load_prompt("scientist")

    user_prompt = f"""以下の占い手法について科学的検証を行ってください。

## 対象占い
{uranai_name}

## リサーチノート
{research_note_path}

## 手順
1. vault_read_note で対象のリサーチノートを読む
2. その占いに関する科学的研究・論文の知識を整理する
   - 占星術ならShawn Carlsonの二重盲検試験(1985, Nature)等
   - バーナム効果、コールドリーディング、確証バイアスの観点
3. vault_write_note で 20_Science/Verdicts/{uranai_name}.md に検証結論ノートを作成
   - 検証ステータス、エビデンスレベル、研究サマリー、結論を含める
4. vault_append_to_note で元のリサーチノートの「## 科学的検証」セクションに検証結果の要約を追記

## 検証ステータスの判定基準
- 効果なし: 複数の質の高い研究で否定
- 一部根拠あり: 限定的な条件下で統計的有意
- 効果あり: 複数の独立した研究で再現性のある効果
- 検証不能: 科学的に検証する方法がない

## 重要
- 科学的誠実さを最優先する
- 出典にはDOIまたはURLを記載する
- 検証不能なものは正直に記す
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
    path = sys.argv[2] if len(sys.argv) > 2 else f"10_Research/East-Asia/{uranai}.md"
    print(run(uranai, path))
