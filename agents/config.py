"""エージェント共通設定"""

import os
from pathlib import Path

# Obsidian Vault パス
VAULT_PATH = Path(
    os.environ.get(
        "OBSIDIAN_VAULT_PATH",
        r"C:\Users\加藤敦也KatoAtsuya\uranai-mura-vault",
    )
)

# GitHub リポジトリ
GITHUB_REPO = "chanceai1234-glitch/uranai-mura"

# モデル設定
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# プロンプトディレクトリ
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(agent_name: str) -> str:
    """エージェントのシステムプロンプトを読み込む。"""
    prompt_file = PROMPTS_DIR / f"{agent_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8")
