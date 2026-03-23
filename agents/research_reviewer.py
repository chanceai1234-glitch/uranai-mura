"""Research Reviewer エージェント

Researcher・Scientistの成果物を品質チェックし、
科学的正確性、情報源の信頼性、網羅性、バイアスの有無を検証する。
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
    note_path: str,
    review_type: str = "research",
) -> dict:
    """Research Reviewerエージェントを実行する。

    Args:
        note_path: レビュー対象のノート相対パス
        review_type: "research" | "science" | "article"

    Returns:
        {"approved": bool, "feedback": str, "issues": list[str]}
    """
    system_prompt = load_prompt("research_reviewer")
    mcp_server = _build_mcp_server()

    checklist = _get_checklist(review_type)

    user_prompt = f"""以下のノートをレビューしてください。

## レビュー対象
{note_path}

## レビュー種別
{review_type}

## 手順
1. vault_read_note で対象ノートを読む
2. 以下のチェックリストに基づいて品質を検証する
3. 問題がなければ承認（approved: true）、問題があれば差し戻し（approved: false）
4. vault_append_to_note で対象ノートの「## レビューログ」セクション（なければ末尾）にレビュー結果を追記

## チェックリスト
{checklist}

## 出力形式
レビューが完了したら、以下のJSON形式で結果を出力してください（最後のメッセージとして）:

```json
{{
  "approved": true/false,
  "feedback": "全体的なフィードバック",
  "issues": ["問題点1", "問題点2"]
}}
```

## 重要
- 批判的思考を持ちつつ、建設的なフィードバックを行う
- 重大な問題（科学的誤り、出典なし）は必ず差し戻し
- 軽微な問題（表現の改善提案等）は承認しつつコメントで指摘
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
                "mcp__obsidian-vault__vault_append_to_note",
                "mcp__obsidian-vault__vault_list_notes",
                "mcp__obsidian-vault__vault_search_notes",
                "mcp__obsidian-vault__vault_get_note_status",
            ],
        ),
    ):
        if hasattr(message, "content"):
            for block in message.content:
                if hasattr(block, "text"):
                    result_text += block.text + "\n"

    # JSONレスポンスをパース
    return _parse_review_result(result_text)


def _get_checklist(review_type: str) -> str:
    """レビュー種別に応じたチェックリストを返す。"""
    checklists = {
        "research": """
- [ ] frontmatterの全フィールドが埋まっているか
- [ ] 概要が正確で偏りがないか
- [ ] 歴史的背景の記述に出典があるか
- [ ] 仕組み・ロジックが実装可能な粒度で記述されているか
- [ ] 地域分類が適切か
- [ ] 文化的・宗教的配慮が適切か
""",
        "science": """
- [ ] 引用された研究は実在するか（DOI/URL確認）
- [ ] エビデンスレベルの評価は適切か
- [ ] 結論は根拠から論理的に導かれているか
- [ ] 反証や限界が記述されているか
- [ ] バーナム効果等の心理メカニズムが考慮されているか
- [ ] 検証ステータスの判定が基準に沿っているか
""",
        "article": """
- [ ] 科学的誠実さが保たれているか（誇張や過度な断定がないか）
- [ ] 一般読者にとってわかりやすいか
- [ ] 出典が明記されているか
- [ ] 文化的配慮が適切か
- [ ] 占いを信じる人を攻撃していないか
""",
    }
    return checklists.get(review_type, checklists["research"])


def _parse_review_result(text: str) -> dict:
    """エージェント出力からレビュー結果のJSONをパースする。"""
    import json
    import re

    # JSONブロックを探す
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # フォールバック: テキスト全体から推測
    approved = "approved" not in text.lower() or '"approved": true' in text.lower()
    return {
        "approved": approved,
        "feedback": text[-500:] if len(text) > 500 else text,
        "issues": [],
    }


if __name__ == "__main__":
    import sys

    note = sys.argv[1] if len(sys.argv) > 1 else "10_Research/East-Asia/四柱推命.md"
    rtype = sys.argv[2] if len(sys.argv) > 2 else "research"
    result = asyncio.run(run(note, rtype))
    print(result)
