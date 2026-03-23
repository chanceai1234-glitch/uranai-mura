"""Writer エージェント

科学検証の結果を元に、一般の人々を啓発する記事・コンテンツを作成する。
"""

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import (
    append_to_note,
    list_notes,
    read_note,
    search_notes,
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
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "vault_write_note": lambda relative_path, frontmatter, body: write_note(
        relative_path, frontmatter, body
    ),
    "vault_list_notes": lambda folder: list_notes(folder),
    "vault_search_notes": lambda query, folder="": search_notes(query, folder),
}


def run(
    uranai_name: str,
    science_note_path: str,
    research_note_path: str = "",
) -> str:
    """Writerエージェントを実行する。

    Args:
        uranai_name: 占い名
        science_note_path: 科学検証ノートの相対パス
        research_note_path: リサーチノートの相対パス（任意）
    """
    system_prompt = load_prompt("writer")

    user_prompt = f"""以下の占い手法について啓発記事を作成してください。

## 対象占い
{uranai_name}

## 参照ノート
- 科学検証ノート: {science_note_path}
{f"- リサーチノート: {research_note_path}" if research_note_path else ""}

## 手順
1. vault_read_note で科学検証ノートとリサーチノートを読む
2. 記事を作成し vault_write_note で 30_Content/Drafts/{uranai_name}.md に保存する

## 記事のフォーマット（frontmatter）
- タイトル: 読者の興味を引くタイトル
- 対象占い: ["{uranai_name}"]
- ステータス: "ドラフト"
- ターゲット読者: "占いに興味がある一般読者"
- tags: [コンテンツ, article, {uranai_name}]

## 記事の構成
1. **導入** (200-300字): 読者の関心を引く問いかけやエピソードから始める
2. **{uranai_name}とは** (300-500字): 占いの仕組みを中立的にわかりやすく解説
3. **科学はどう見ているか** (400-600字): エビデンスに基づく検証結果。論文の引用を含む
4. **なぜ「当たる」と感じるのか** (300-500字): バーナム効果・確証バイアス等の心理メカニズム
5. **まとめ — 占いとの付き合い方** (200-300字): 断定を避け、読者自身が考えられる形で締める

## トーン・スタイル
- 親しみやすく、でも軽薄にならない
- 「占いはデタラメ」ではなく「科学はこう言っている」というスタンス
- 占いを信じる人を攻撃しない。理解と共感をベースに
- 専門用語には必ず平易な補足を付ける
- 適度にユーモアを交えてよいが、皮肉は避ける
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
    science = sys.argv[2] if len(sys.argv) > 2 else f"20_Science/Verdicts/{uranai}.md"
    research = sys.argv[3] if len(sys.argv) > 3 else f"10_Research/East-Asia/{uranai}.md"
    print(run(uranai, science, research))
