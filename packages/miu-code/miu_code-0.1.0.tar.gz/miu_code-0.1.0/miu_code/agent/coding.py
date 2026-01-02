"""Coding agent implementation."""

from miu_code.session.storage import SessionStorage
from miu_code.tools import get_all_tools
from miu_core.agents import AgentConfig, ReActAgent
from miu_core.models import Response
from miu_core.providers import create_provider
from miu_core.tools import Tool, ToolRegistry

SYSTEM_PROMPT = """You are a helpful AI coding assistant. You can read, write, and edit files, \
run shell commands, and search through codebases.

When helping with coding tasks:
1. First understand the request clearly
2. Use tools to explore the codebase if needed
3. Make minimal, focused changes
4. Verify your changes work when possible

Be concise and direct in your responses."""


class CodingAgent:
    """High-level coding agent with session persistence."""

    def __init__(
        self,
        model: str = "anthropic:claude-sonnet-4-20250514",
        working_dir: str = ".",
        session_id: str | None = None,
    ) -> None:
        self.provider = create_provider(model)
        self.tools = ToolRegistry()
        self.working_dir = working_dir
        self.session = SessionStorage(session_id=session_id, working_dir=working_dir)

        # Register all tools
        for tool in get_all_tools():
            self.tools.register(tool)

        # Create ReAct agent
        config = AgentConfig(
            system_prompt=SYSTEM_PROMPT,
            max_iterations=20,
        )
        self._agent = ReActAgent(
            provider=self.provider,
            tools=self.tools,
            config=config,
            working_dir=working_dir,
        )

        # Load session if exists
        messages = self.session.load()
        for msg in messages:
            self._agent.memory.add(msg)

    async def run(self, query: str) -> Response:
        """Run a query and persist session."""
        response = await self._agent.run(query)

        # Save updated session
        self.session.save(self._agent.memory.messages)

        return response

    def get_tools(self) -> list[Tool]:
        """Get all registered tools.

        Returns:
            List of registered tools
        """
        return list(self.tools)
