"""Implementer エージェント

設計書に基づきコードを実装し、ファイルとして出力する。
"""

import os
from pathlib import Path

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import read_note

# src/ ディレクトリのパス（コンテナ内）
SRC_DIR = Path(os.environ.get("SRC_DIR", "/app/src"))


def _write_file(relative_path: str, content: str) -> str:
    """src/ 配下にファイルを書き込む。"""
    file_path = SRC_DIR / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Written: {file_path}"


def _read_file(relative_path: str) -> str:
    """src/ 配下のファイルを読み取る。"""
    file_path = SRC_DIR / relative_path
    if not file_path.exists():
        return f"Error: File not found: {file_path}"
    return file_path.read_text(encoding="utf-8")


def _list_files(folder: str = "") -> list[str]:
    """src/ 配下のファイル一覧を返す。"""
    search_path = SRC_DIR / folder if folder else SRC_DIR
    if not search_path.exists():
        return []
    return [str(p.relative_to(SRC_DIR)) for p in search_path.rglob("*.py")]


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
        "name": "write_code",
        "description": "src/配下にPythonコードファイルを作成する",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "src/からの相対パス (例: uranai/shichusuimei.py)",
                },
                "content": {"type": "string", "description": "ファイルの内容"},
            },
            "required": ["relative_path", "content"],
        },
    },
    {
        "name": "read_code",
        "description": "src/配下のコードファイルを読み取る",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string", "description": "src/からの相対パス"},
            },
            "required": ["relative_path"],
        },
    },
    {
        "name": "list_code_files",
        "description": "src/配下のPythonファイル一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "サブフォルダ（空=全体）"},
            },
            "required": [],
        },
    },
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "write_code": lambda relative_path, content: _write_file(relative_path, content),
    "read_code": lambda relative_path: _read_file(relative_path),
    "list_code_files": lambda folder="": _list_files(folder),
}


def run(uranai_name: str, architecture_path: str = "") -> str:
    """Implementerを実行する。"""
    system_prompt = load_prompt("implementer")
    arch_path = architecture_path or f"40_Platform/Architecture/{uranai_name}.md"

    user_prompt = f"""以下の設計書に基づき、{uranai_name}の占いロジックを実装してください。

## 設計書
{arch_path}

## 手順
1. vault_read_note で設計書を読む
2. list_code_files で既存のコードを確認
3. write_code で src/ 配下にコードを実装

## 実装するもの
1. **占いロジックモジュール**: src/uranai/ 配下に占い名に対応するファイル（例: shichusuimei.py）
   - 入力バリデーション
   - 占い計算ロジック
   - 結果の構造化出力
2. **共通インターフェース**: src/uranai/base.py（未作成の場合）
   - 全占いが実装する共通の基底クラス/プロトコル
3. **__init__.py**: src/uranai/__init__.py

## コーディング規約
- 型ヒントを必ず付ける
- docstringは日本語OK
- 関数は単一責任を守る
- マスタデータはコード内に定数として定義（小規模の場合）またはJSONファイルとして分離
- セキュリティ: 入力値のバリデーションを必ず行う
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
