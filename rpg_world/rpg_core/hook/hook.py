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
        """Remove system messages from context."""
        context.messages = [msg for msg in context.messages if msg.get("role") != "system"]

    def on_build_runtime_context(self, channel: str, chat_id: str, timezone: str, runtime_ctx: str) -> str:
        """Inject RPG World context into the runtime context."""
        return f"{runtime_ctx}\n\n[RPG World: {self.world_name}]"
