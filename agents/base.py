"""エージェント基盤: anthropic SDK のツール使用ループを共通化する。

各エージェントは以下を定義するだけで良い:
  - system_prompt
  - tools (関数定義)
  - tool_handlers (関数名 → Python関数)
"""

from __future__ import annotations

import json
from typing import Any, Callable

import anthropic

from agents.config import DEFAULT_MODEL


def run_agent_loop(
    *,
    system_prompt: str,
    user_prompt: str,
    tools: list[dict],
    tool_handlers: dict[str, Callable[..., Any]],
    model: str = DEFAULT_MODEL,
    max_turns: int = 20,
) -> str:
    """ツール使用ループを実行し、最終テキスト応答を返す。

    Claude がツール呼び出しを返す限りループし、
    テキスト応答を返したら終了する。
    """
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 環境変数を自動で使う

    messages: list[dict] = [{"role": "user", "content": user_prompt}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        # 応答をメッセージ履歴に追加
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        # ツール呼び出しがあるか確認
        tool_uses = [b for b in assistant_content if b.type == "tool_use"]

        if not tool_uses:
            # テキスト応答のみ → 完了
            text_parts = [b.text for b in assistant_content if hasattr(b, "text")]
            return "\n".join(text_parts)

        # ツール呼び出しを実行
        tool_results = []
        for tool_use in tool_uses:
            handler = tool_handlers.get(tool_use.name)
            if handler:
                try:
                    result = handler(**tool_use.input)
                    result_str = json.dumps(result, ensure_ascii=False, indent=2) if isinstance(result, (dict, list)) else str(result)
                except Exception as e:
                    result_str = f"Error: {e}"
            else:
                result_str = f"Error: Unknown tool '{tool_use.name}'"

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})

    return "Error: max_turns reached without final response"
