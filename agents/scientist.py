"""Scientist エージェント

各占い手法に対する科学的研究・メタ分析・実験結果を収集し、
効果の有無を客観的に評価する。
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
    return create_sdk_mcp_server(
        name="obsidian-vault",
        version="1.0.0",
        tools=ALL_VAULT_TOOLS,
    )


async def run(
    uranai_name: str,
    research_note_path: str,
) -> str:
    """Scientistエージェントを実行する。

    Args:
        uranai_name: 占い名
        research_note_path: リサーチノートの相対パス（例: "10_Research/East-Asia/四柱推命.md"）

    Returns:
        エージェントの最終出力テキスト
    """
    system_prompt = load_prompt("scientist")
    mcp_server = _build_mcp_server()

    user_prompt = f"""以下の占い手法について科学的検証を行ってください。

## 対象占い
{uranai_name}

## リサーチノート
{research_note_path}

## 手順
1. vault_read_note で対象のリサーチノートを読む
2. Web検索で科学的研究・論文を探す
   - Google Scholar、PubMed、学術データベースを優先
   - 検索キーワード例: "{uranai_name} scientific study", "{uranai_name} evidence", "{uranai_name} debunk"
3. vault_write_note で 20_Science/Verdicts/{uranai_name}.md に検証結論ノートを作成
   - テンプレート（90_Templates/T_Science.md）のフォーマットに従う
   - エビデンスレベルを明示する
4. vault_append_to_note で元のリサーチノートの「## 科学的検証」セクションに要約を追記
5. リサーチノートの frontmatter の「科学検証ステータス」を更新

## 検証ステータスの判定基準
- 効果なし: 複数の質の高い研究で否定
- 一部根拠あり: 限定的な条件下で統計的有意な結果
- 効果あり: 複数の独立した研究で再現性のある効果
- 検証不能: 科学的に検証する方法がない
- 検証中: 調査進行中

## 重要
- 科学的誠実さを最優先する
- バーナム効果、コールドリーディング、確証バイアスを考慮する
- 出典は必ずDOIまたはURLを記載する
- 検証不能なものは正直に「検証不能」と記す
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
                "mcp__obsidian-vault__vault_append_to_note",
                "mcp__obsidian-vault__vault_list_notes",
                "mcp__obsidian-vault__vault_get_note_status",
            ],
        ),
    ):
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "text"):
                    result_text += block.text + "\n"

    return result_text


if __name__ == "__main__":
    import sys

    uranai = sys.argv[1] if len(sys.argv) > 1 else "四柱推命"
    path = sys.argv[2] if len(sys.argv) > 2 else f"10_Research/East-Asia/{uranai}.md"
    result = asyncio.run(run(uranai, path))
    print(result)
