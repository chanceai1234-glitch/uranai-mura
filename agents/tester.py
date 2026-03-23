"""Tester エージェント

テストケースの設計、テストコードの実装、テストの実行を行う。
"""

import os
import subprocess
from pathlib import Path

from agents.base import run_agent_loop
from agents.config import load_prompt
from agents.tools.obsidian import read_note

SRC_DIR = Path(os.environ.get("SRC_DIR", "/app/src"))
TESTS_DIR = Path(os.environ.get("TESTS_DIR", "/app/tests"))


def _write_test(relative_path: str, content: str) -> str:
    """tests/ 配下にテストファイルを書き込む。"""
    file_path = TESTS_DIR / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Written: {file_path}"


def _read_file(relative_path: str, base: str = "src") -> str:
    """ファイルを読み取る。"""
    base_dir = SRC_DIR if base == "src" else TESTS_DIR
    file_path = base_dir / relative_path
    if not file_path.exists():
        return f"Error: File not found: {file_path}"
    return file_path.read_text(encoding="utf-8")


def _list_files(folder: str = "", base: str = "src") -> list[str]:
    """ファイル一覧を返す。"""
    base_dir = SRC_DIR if base == "src" else TESTS_DIR
    search_path = base_dir / folder if folder else base_dir
    if not search_path.exists():
        return []
    return [str(p.relative_to(base_dir)) for p in search_path.rglob("*.py")]


def _run_tests(test_path: str = "") -> str:
    """pytestを実行してテスト結果を返す。"""
    cmd = ["python", "-m", "pytest", "-v"]
    if test_path:
        cmd.append(str(TESTS_DIR / test_path))
    else:
        cmd.append(str(TESTS_DIR))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Test execution timed out (120s)"
    except Exception as e:
        return f"Error running tests: {e}"


TOOLS = [
    {
        "name": "vault_read_note",
        "description": "Obsidian Vaultからノート（要件定義書等）を読み取る",
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
        "name": "list_source_files",
        "description": "src/配下のPythonファイル一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {"type": "string", "description": "サブフォルダ（空=全体）"},
            },
            "required": [],
        },
    },
    {
        "name": "write_test",
        "description": "tests/配下にテストファイルを作成する",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "tests/からの相対パス (例: test_shichusuimei.py)",
                },
                "content": {"type": "string", "description": "テストコードの内容"},
            },
            "required": ["relative_path", "content"],
        },
    },
    {
        "name": "run_tests",
        "description": "pytestを実行してテスト結果を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "実行するテストファイルのパス（空=全テスト）",
                },
            },
            "required": [],
        },
    },
]

TOOL_HANDLERS = {
    "vault_read_note": lambda relative_path: read_note(relative_path),
    "read_source": lambda relative_path: _read_file(relative_path, "src"),
    "list_source_files": lambda folder="": _list_files(folder, "src"),
    "write_test": lambda relative_path, content: _write_test(relative_path, content),
    "run_tests": lambda test_path="": _run_tests(test_path),
}


def run(uranai_name: str, requirement_path: str = "") -> str:
    """Testerを実行する。"""
    system_prompt = load_prompt("tester")
    req_path = requirement_path or f"40_Platform/Requirements/{uranai_name}.md"

    user_prompt = f"""以下の占いロジックのテストを設計・実装・実行してください。

## 対象
{uranai_name}

## 参照
- 要件定義書: {req_path}

## 手順
1. vault_read_note で要件定義書を読み、受け入れ条件を確認する
2. list_source_files で実装コードを確認する
3. read_source で対象コードを読む
4. write_test でテストコードを作成
5. run_tests でテストを実行し結果を確認
6. 失敗したテストがあれば原因を分析して報告

## テストに含めるべきもの
1. **正常系テスト**: 有効な入力での期待出力
2. **異常系テスト**: 無効な入力（不正な日付、範囲外の値等）
3. **境界値テスト**: 節気の境界、日付の境界等
4. **出力フォーマットテスト**: レスポンスの構造が仕様通りか

## テストの書き方
- pytest を使用
- テスト名は日本語コメントで意図を説明
- 1テスト1アサーションを原則とする
- fixtureを活用してテストデータを整理する
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
