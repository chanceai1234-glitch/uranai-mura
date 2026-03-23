"""Researcher エージェント

世界中の占い手法を網羅的に収集・分類し、
Obsidian Vaultに構造化されたノートとして記録する。
"""

import asyncio

from claude_agent_sdk import (
    ClaudeAgentOptions,
    create_sdk_mcp_server,
    query,
)

from agents.config import load_prompt
from agents.tools.obsidian_tools import ALL_VAULT_TOOLS


def _build_mcp_server():
    """Obsidian Vault操作用のMCPサーバーを構築する。"""
    return create_sdk_mcp_server(
        name="obsidian-vault",
        version="1.0.0",
        tools=ALL_VAULT_TOOLS,
    )


async def run(
    target: str,
    existing_data: str = "",
) -> str:
    """Researcherエージェントを実行する。

    Args:
        target: 調査対象（占い名、地域名など）
        existing_data: 既存のリサーチデータ（あれば渡す）

    Returns:
        エージェントの最終出力テキスト
    """
    system_prompt = load_prompt("researcher")
    mcp_server = _build_mcp_server()

    user_prompt = f"""以下の占い手法について調査し、Obsidian Vaultにリサーチノートを作成してください。

## 調査対象
{target}

## 既存データ
{existing_data if existing_data else "（なし）"}

## 手順
1. まず vault_list_notes で 10_Research/ 配下に既存ノートがないか確認
2. Web検索で情報を収集
3. vault_write_note で 10_Research/{{地域}}/ 配下にノートを作成
   - テンプレート（90_Templates/T_Research.md）のフォーマットに従う
   - frontmatterの全フィールドを埋める
   - 科学検証ステータスは「未検証」にする

## 注意
- 情報源は信頼性の高いものを優先
- 文化的・宗教的背景を尊重し、偏見なく記述
- 不確かな情報には「要確認」を付ける
"""

    result_text = ""
    async for message in query(
        prompt=user_prompt,
        options=ClaudeAgentOptions(
            system_prompt=system_prompt,
            mcp_servers={"obsidian-vault": mcp_server},
            allowed_tools=[
                "WebSearch",
                "WebFetch",
                "mcp__obsidian-vault__vault_read_note",
                "mcp__obsidian-vault__vault_write_note",
                "mcp__obsidian-vault__vault_list_notes",
                "mcp__obsidian-vault__vault_search_notes",
            ],
        ),
    ):
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "text"):
                    result_text += block.text + "\n"

    return result_text


async def run_batch(targets: list[str], existing_data: str = "") -> list[str]:
    """複数の占い手法を並列で調査する。

    Args:
        targets: 調査対象のリスト
        existing_data: 既存のリサーチデータ

    Returns:
        各調査の結果テキストのリスト
    """
    tasks = [run(target, existing_data) for target in targets]
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "四柱推命"
    result = asyncio.run(run(target))
    print(result)
