"""Architect エージェント

要件定義を元にシステム設計・API設計・DB設計を行う。
"""

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import list_notes, read_note, write_note

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
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "vault_write_note": lambda relative_path, frontmatter, body: write_note(
        relative_path, frontmatter, body
    ),
    "vault_list_notes": lambda folder: list_notes(folder),
}


def run(uranai_name: str, requirement_path: str = "") -> str:
    """Architectを実行する。"""
    system_prompt = load_prompt("architect")
    req_path = requirement_path or f"40_Platform/Requirements/{uranai_name}.md"

    user_prompt = f"""以下の要件定義を元にシステム設計を行ってください。

## 対象
{uranai_name} 体験機能

## 要件定義書
{req_path}

## 手順
1. vault_read_note で要件定義書を読む
2. システム設計書を作成し vault_write_note で 40_Platform/Architecture/{uranai_name}.md に保存

## 設計書に含めるべき内容
1. **システム構成図**（テキストで表現）
2. **API設計**
   - エンドポイント一覧（メソッド、パス、説明）
   - リクエスト/レスポンスのJSON例
3. **データモデル**
   - 必要なテーブル/コレクションとフィールド定義
4. **占いロジックモジュール設計**
   - 入力→中間処理→出力のパイプライン
   - マスタデータの構造
5. **技術選定と理由**
   - フレームワーク、DB、フロントエンドの選定
6. **トレードオフ・検討事項**

## 設計書のfrontmatter
- 設計名: "{uranai_name}体験機能 設計書"
- 対象要件: ["{req_path}"]
- ステータス: "ドラフト"
- tags: [設計, architecture, {uranai_name}]

## 設計原則
- シンプルさを優先。過度なエンジニアリングを避ける
- 占いロジックはプラグイン型にし、他の占いも同じインターフェースで追加できるようにする
- 結果画面には必ず「この占いの科学的検証」へのリンクを配置する
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
    print(run(uranai))
