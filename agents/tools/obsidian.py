"""Obsidian Vault 読み書きツール

エージェントがObsidian VaultのMarkdownファイルを操作するためのツール群。
Obsidian APIは使わず、ファイルシステムを直接操作する。
"""

import os
import re
from pathlib import Path

import yaml

# Vault パスは環境変数または設定ファイルから取得
VAULT_PATH = Path(
    os.environ.get(
        "OBSIDIAN_VAULT_PATH",
        r"C:\Users\加藤敦也KatoAtsuya\uranai-mura-vault",
    )
)


def _ensure_vault() -> Path:
    """Vaultパスの存在を確認する。"""
    if not VAULT_PATH.exists():
        raise FileNotFoundError(f"Obsidian Vault not found: {VAULT_PATH}")
    return VAULT_PATH


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Markdownファイルからfrontmatterとbodyを分離する。"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        frontmatter = yaml.safe_load(match.group(1)) or {}
        body = match.group(2)
        return frontmatter, body
    return {}, content


def _compose_frontmatter(frontmatter: dict, body: str) -> str:
    """frontmatterとbodyからMarkdownファイルの内容を構成する。"""
    if frontmatter:
        fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).strip()
        return f"---\n{fm_str}\n---\n\n{body}"
    return body


def read_note(relative_path: str) -> dict:
    """ノートを読み取り、frontmatterとbodyを返す。

    Args:
        relative_path: Vaultルートからの相対パス（例: "10_Research/East-Asia/四柱推命.md"）

    Returns:
        {"frontmatter": dict, "body": str, "path": str}
    """
    vault = _ensure_vault()
    file_path = vault / relative_path
    if not file_path.exists():
        raise FileNotFoundError(f"Note not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)
    return {"frontmatter": frontmatter, "body": body, "path": str(file_path)}


def write_note(relative_path: str, frontmatter: dict, body: str) -> str:
    """ノートを作成または上書きする。

    Args:
        relative_path: Vaultルートからの相対パス
        frontmatter: YAMLフロントマターの辞書
        body: Markdownの本文

    Returns:
        書き込んだファイルの絶対パス
    """
    vault = _ensure_vault()
    file_path = vault / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    content = _compose_frontmatter(frontmatter, body)
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def append_to_note(relative_path: str, section: str, text: str) -> str:
    """既存ノートの指定セクションにテキストを追記する。

    Args:
        relative_path: Vaultルートからの相対パス
        section: 追記先のセクション見出し（例: "## 科学的検証"）
        text: 追記するテキスト

    Returns:
        書き込んだファイルの絶対パス
    """
    vault = _ensure_vault()
    file_path = vault / relative_path
    if not file_path.exists():
        raise FileNotFoundError(f"Note not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    # セクションを探して直後に追記
    pattern = re.compile(rf"(^{re.escape(section)}\s*\n)", re.MULTILINE)
    match = pattern.search(content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + "\n" + text + "\n" + content[insert_pos:]
    else:
        # セクションが見つからない場合は末尾に追加
        content += f"\n\n{section}\n\n{text}\n"

    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def list_notes(folder: str, recursive: bool = True) -> list[str]:
    """指定フォルダ内のMarkdownファイル一覧を返す。

    Args:
        folder: Vaultルートからの相対フォルダパス（例: "10_Research/East-Asia"）
        recursive: サブフォルダも含めるか

    Returns:
        相対パスのリスト
    """
    vault = _ensure_vault()
    folder_path = vault / folder
    if not folder_path.exists():
        return []

    pattern = "**/*.md" if recursive else "*.md"
    return [str(p.relative_to(vault)) for p in folder_path.glob(pattern)]


def search_notes(query: str, folder: str = "") -> list[dict]:
    """ノートの内容を全文検索する。

    Args:
        query: 検索クエリ（正規表現）
        folder: 検索対象フォルダ（空の場合はVault全体）

    Returns:
        マッチしたノートのリスト [{"path": str, "matches": list[str]}]
    """
    vault = _ensure_vault()
    search_path = vault / folder if folder else vault
    results = []
    pattern = re.compile(query, re.IGNORECASE)

    for md_file in search_path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        matches = pattern.findall(content)
        if matches:
            results.append({
                "path": str(md_file.relative_to(vault)),
                "matches": matches[:10],  # 最大10件
            })

    return results


def get_note_status(relative_path: str) -> dict:
    """ノートのfrontmatterからステータス情報を抽出する。

    Args:
        relative_path: Vaultルートからの相対パス

    Returns:
        frontmatterの辞書（ステータス関連フィールド）
    """
    note = read_note(relative_path)
    fm = note["frontmatter"]
    return {
        "path": relative_path,
        "科学検証ステータス": fm.get("科学検証ステータス", "不明"),
        "ステータス": fm.get("ステータス", "不明"),
        "tags": fm.get("tags", []),
        "updated": fm.get("updated", "不明"),
    }
