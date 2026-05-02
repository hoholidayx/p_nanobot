"""RPG World — an example AgentHook implementation.

Demonstrates how to hook into the nanobot agent lifecycle:
  - ``on_system_prompt_built`` — inspect/modify the system prompt
    assembled from AGENTS.md, SOUL.md, USER.md, TOOLS.md, etc.
  - ``before_iteration`` — observe or alter messages just before
    they are sent to the LLM.
"""

from rpg_world.hook import RpgWorldHook

__all__ = ["RpgWorldHook"]
