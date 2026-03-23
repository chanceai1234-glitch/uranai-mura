"""Obsidian Vault ツールのユニットテスト"""

import tempfile
from pathlib import Path

import pytest

# テスト時は一時ディレクトリをVaultとして使う
import agents.tools.obsidian as obsidian_mod


@pytest.fixture(autouse=True)
def temp_vault(tmp_path):
    """テスト用の一時Vaultを作成し、モジュールのVAULT_PATHを差し替える。"""
    # フォルダ構造を作成
    (tmp_path / "10_Research" / "East-Asia").mkdir(parents=True)
    (tmp_path / "20_Science" / "Verdicts").mkdir(parents=True)
    (tmp_path / "90_Templates").mkdir(parents=True)

    # VAULT_PATHを一時ディレクトリに差し替え
    original = obsidian_mod.VAULT_PATH
    obsidian_mod.VAULT_PATH = tmp_path
    yield tmp_path
    obsidian_mod.VAULT_PATH = original


class TestWriteAndReadNote:
    def test_write_and_read(self, temp_vault):
        fm = {"占い名": "テスト占い", "地域": "East-Asia", "tags": ["test"]}
        body = "## 概要\n\nこれはテストです。"

        path = obsidian_mod.write_note("10_Research/East-Asia/テスト占い.md", fm, body)
        assert Path(path).exists()

        result = obsidian_mod.read_note("10_Research/East-Asia/テスト占い.md")
        assert result["frontmatter"]["占い名"] == "テスト占い"
        assert "テストです" in result["body"]

    def test_read_nonexistent(self, temp_vault):
        with pytest.raises(FileNotFoundError):
            obsidian_mod.read_note("nonexistent.md")


class TestAppendToNote:
    def test_append_to_existing_section(self, temp_vault):
        fm = {"占い名": "テスト"}
        body = "## 概要\n\n概要テキスト\n\n## 科学的検証\n\n（未記入）\n\n## 参考文献\n"
        obsidian_mod.write_note("10_Research/East-Asia/テスト.md", fm, body)

        obsidian_mod.append_to_note(
            "10_Research/East-Asia/テスト.md",
            "## 科学的検証",
            "バーナム効果の研究により効果なしと判定。",
        )

        result = obsidian_mod.read_note("10_Research/East-Asia/テスト.md")
        assert "バーナム効果" in result["body"]

    def test_append_to_nonexistent_section(self, temp_vault):
        fm = {"占い名": "テスト"}
        body = "## 概要\n\n概要テキスト\n"
        obsidian_mod.write_note("10_Research/East-Asia/テスト.md", fm, body)

        obsidian_mod.append_to_note(
            "10_Research/East-Asia/テスト.md",
            "## 新セクション",
            "新しい内容です。",
        )

        result = obsidian_mod.read_note("10_Research/East-Asia/テスト.md")
        assert "新しい内容です" in result["body"]


class TestListNotes:
    def test_list_empty_folder(self, temp_vault):
        notes = obsidian_mod.list_notes("10_Research/East-Asia")
        assert notes == []

    def test_list_with_notes(self, temp_vault):
        obsidian_mod.write_note("10_Research/East-Asia/a.md", {}, "a")
        obsidian_mod.write_note("10_Research/East-Asia/b.md", {}, "b")

        notes = obsidian_mod.list_notes("10_Research/East-Asia")
        assert len(notes) == 2
        assert any("a.md" in n for n in notes)
        assert any("b.md" in n for n in notes)


class TestSearchNotes:
    def test_search_finds_match(self, temp_vault):
        obsidian_mod.write_note("10_Research/East-Asia/四柱推命.md", {}, "干支・五行・十神で占う")

        results = obsidian_mod.search_notes("五行", "10_Research")
        assert len(results) == 1
        assert "四柱推命" in results[0]["path"]

    def test_search_no_match(self, temp_vault):
        obsidian_mod.write_note("10_Research/East-Asia/四柱推命.md", {}, "干支で占う")

        results = obsidian_mod.search_notes("タロット", "10_Research")
        assert len(results) == 0


class TestGetNoteStatus:
    def test_get_status(self, temp_vault):
        fm = {"占い名": "テスト", "科学検証ステータス": "未検証", "tags": ["test"]}
        obsidian_mod.write_note("10_Research/East-Asia/テスト.md", fm, "body")

        status = obsidian_mod.get_note_status("10_Research/East-Asia/テスト.md")
        assert status["科学検証ステータス"] == "未検証"
        assert "test" in status["tags"]
