# miu-code

AI coding agent with CLI and TUI. Provides an intelligent assistant for code exploration, generation, and manipulation through both command-line and terminal UI interfaces.

## Quick Start

### Installation

```bash
uv add miu-code
```

### Usage

**CLI Mode (one-shot query):**
```bash
miu "read package.json"
miu -q "what's in the main.py file?"
miu --model openai:gpt-4o "help me debug this"
```

**CLI Mode (interactive REPL):**
```bash
miu
```

**TUI Mode (Terminal UI):**
```bash
miu-tui
```

## Features

### Code Tools
- **Read** - View file contents
- **Write** - Create new files
- **Edit** - Modify specific lines in files
- **Glob** - Pattern-based file discovery
- **Grep** - Content-based search
- **Bash** - Execute shell commands

### Intelligence
- Powered by Claude Sonnet (or your chosen model)
- Multi-model support: Anthropic, OpenAI, Google, etc.
- ReAct reasoning with up to 20 iterations
- Session persistence across conversations

### Interfaces
- **TUI** - Responsive terminal UI with Textual framework
  - Real-time streaming with auto-scroll
  - Interruptible agent (Escape key)
  - Mode system (ASK, NORMAL, PLAN) with safety levels
  - Tool approval dialogs
  - Message history navigation

- **CLI** - Fast, scriptable command-line interface
  - One-shot queries for automation
  - Interactive REPL for exploration
  - Slash command support (/cook, /commit, /plan)
  - ACP server mode for editor integration

## Architecture

```
miu-code/
├── agent/        → CodingAgent with ReAct reasoning
├── tools/        → Code manipulation tools (read, write, edit, etc.)
├── cli/          → asyncclick-based CLI entry point
├── tui/          → Textual-based Terminal UI
├── acp/          → Agent Communication Protocol server
├── session/      → Conversation persistence
└── commands/     → Slash command handlers
```

## Configuration

### Model Selection

Default: `anthropic:claude-sonnet-4-20250514`

Supported providers:
```bash
miu -m "anthropic:claude-opus-4-20251105" -q "your query"
miu -m "openai:gpt-4o" -q "your query"
miu -m "google:gemini-2.0-flash" -q "your query"
```

### Session Management

```bash
miu -s session-123      # Resume session
miu --session new-id    # Create new session
```

### ACP Integration

```bash
miu --acp               # Start ACP server for editor integration
```

## TUI Key Bindings

| Key | Action |
|-----|--------|
| Ctrl+C | Quit |
| Ctrl+N | New session |
| Ctrl+L | Clear chat |
| Escape | Interrupt / Focus input |
| Shift+Tab | Cycle mode |
| Shift+Up/Down | Scroll chat |
| Up/Down (in input) | History navigation |
| Enter | Submit message |

## Safety & Security

- Path traversal protection for file operations
- Tool approval system in TUI mode
- Configurable safety modes:
  - **ASK** - Request approval for all tool use
  - **NORMAL** - Auto-approve safe tools
  - **PLAN** - Planning mode with warnings

## Documentation

- [Project Overview & PDR](./docs/project-overview-pdr.md)
- [Code Standards](./docs/code-standards.md)
- [System Architecture](./docs/system-architecture.md)
- [Codebase Summary](./docs/codebase-summary.md)
- [TUI Design Guide](./docs/tui-design.md)
- [Project Roadmap](./docs/project-roadmap.md)

## Development

**Python:** >=3.11
**License:** MIT

### Key Dependencies
- `miu-core[anthropic]` - Agent framework
- `textual>=1.0.0` - TUI framework
- `asyncclick>=8.1` - Async CLI
- `rich>=13.0` - Rich terminal output
- `prompt-toolkit>=3.0` - Advanced input handling

## Contributing

1. Follow [Code Standards](./docs/code-standards.md)
2. Run tests: `pytest tests/`
3. Check formatting: `ruff format .`
4. Type check: `mypy miu_code/`

## Support

- Issues: GitHub issues
- Documentation: See `/docs` folder
- Examples: Check `/miu_code/commands` for slash command patterns
