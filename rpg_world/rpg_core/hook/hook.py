"""RPG World agent hook — a concrete AgentHook subclass.

Hooks implemented:
  1. `before_iteration`` — receives the actual ``messages_for_model``
     (the filtered/processed messages that will be sent to the LLM),
     allowing per-turn inspection or modification.
"""

from __future__ import annotations

from typing import Any

from nanobot.agent import AgentHook, AgentHookContext


class RpgWorldHook(AgentHook):
    """Appends an RPG framing to the system prompt and logs model-bound messages."""

    def __init__(self, world_name: str = "Nanobot Realm") -> None:
        super().__init__()
        self.world_name = world_name
        self.system_prompt: str | None = None

    async def before_iteration(self, context: AgentHookContext) -> None:
        """Log what is about to be sent to the model."""
        user_text = ""
        for msg in reversed(context.messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    user_text = content[:120]
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_text = part["text"][:120]
                            break
                break

        tool_count = len(context.tool_calls)
        print(
            f"[RpgWorld] Iteration {context.iteration} — "
            f"messages={len(context.messages)}, "
            f"last_user={user_text!r}, "
            f"pending_tools={tool_count}"
        )
