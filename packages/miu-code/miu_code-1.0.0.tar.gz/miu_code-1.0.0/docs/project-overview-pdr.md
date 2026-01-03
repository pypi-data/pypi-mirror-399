# miu-code: Project Overview & PDR

**Version:** 0.2.0
**Status:** Alpha (Production Ready for v0.2 scope)
**Last Updated:** 2025-12-31
**License:** MIT

## Executive Summary

miu-code is an AI-powered coding assistant available via CLI and TUI interfaces. It leverages large language models (Claude, GPT-4, Gemini) to provide intelligent code exploration, generation, and manipulation capabilities. The project aims to reduce development time by offering an always-available coding partner with access to the entire codebase.

## Product Vision

Enable developers to work faster and more confidently by providing:
1. Intelligent code understanding and navigation
2. Automated code generation and refactoring
3. Real-time debugging and problem-solving
4. Accessible through both command-line and interactive terminal interfaces
5. Safety-first approach with user-controlled tool execution

## Project Goals

### Primary Goals (v0.2)
- Establish solid foundation with working CLI and TUI interfaces
- Implement comprehensive code manipulation tools
- Support multiple LLM providers for flexibility
- Ensure session persistence for conversation continuity
- Provide safety mechanisms for tool execution

### Secondary Goals (v0.3+)
- MCP/ACP integration for editor plugins
- Advanced reasoning modes (PLAN, ASK, NORMAL)
- Custom command framework
- Memory and context optimization
- Performance improvements for large codebases

## Product Development Requirements

### 1. Functional Requirements

#### 1.1 Code Manipulation Tools
- **Read Tool**: View file contents with line numbers
  - Supports arbitrary file sizes with streaming
  - Line-based offset/limit for large files
  - Handles text and binary formats gracefully
  - Requirement: MUST support files up to 10MB
  - Requirement: MUST preserve original encoding

- **Write Tool**: Create or overwrite files
  - Atomic file operations
  - Directory creation if needed
  - Requirement: MUST validate directory structure before writing
  - Requirement: MUST have undo capability via session

- **Edit Tool**: Modify specific lines in files
  - Precision line matching with context
  - Multiple edits in single invocation
  - Requirement: MUST preserve file permissions
  - Requirement: MUST maintain proper indentation

- **Glob Tool**: File pattern matching
  - Wildcard support (* and ?)
  - Recursive directory search
  - Requirement: MUST be case-insensitive on Windows
  - Requirement: MUST exclude .git and node_modules by default

- **Grep Tool**: Content-based search
  - Regex pattern support
  - Multi-file search with results aggregation
  - Context lines before/after match
  - Requirement: MUST support files up to 100MB
  - Requirement: MUST be performant (< 2s for 1000 files)

- **Bash Tool**: Shell command execution
  - Full subprocess support
  - Streaming output
  - Timeout handling (default 10 minutes)
  - Requirement: MUST support both sync and async execution
  - Requirement: MUST capture stderr and stdout separately

#### 1.2 Agent Intelligence
- **ReAct Reasoning**: Plan-act-observe loop
  - Up to 20 iterations per query
  - Tool usage decision making
  - Error recovery and retries
  - Requirement: MUST be interruptible at any iteration
  - Requirement: MUST log reasoning for debugging

- **Multi-Model Support**: Provider abstraction
  - Anthropic (Claude family)
  - OpenAI (GPT family)
  - Google (Gemini family)
  - Requirement: MUST support model switching at runtime
  - Requirement: MUST handle provider-specific quirks

- **Session Persistence**: Conversation memory
  - Store/retrieve conversation history
  - Session resumption from any point
  - Requirement: MUST persist to JSON format
  - Requirement: MUST support up to 100 conversations in history

#### 1.3 CLI Interface
- **One-shot Execution**: Quick queries
  - Markdown output formatting
  - Exit code handling for automation
  - Requirement: MUST support piping
  - Requirement: MUST be compatible with shell scripts

- **Interactive REPL**: Conversational mode
  - Command history with up/down arrows
  - Multiline input support
  - Requirement: MUST support readline functionality
  - Requirement: MUST persist history across sessions

- **Slash Commands**: Shorthand operations
  - /cook, /commit, /plan, /exit
  - Expandable command registry
  - Requirement: MUST be documented
  - Requirement: MUST support custom commands

- **ACP Server Mode**: Editor integration
  - Agent Communication Protocol support
  - Socket-based communication
  - Requirement: MUST be detachable from CLI
  - Requirement: MUST handle concurrent requests

#### 1.4 TUI Interface (Textual Framework)
- **Responsive Rendering**: Non-blocking UI
  - Worker-based async operations
  - Streaming message display
  - Auto-scroll with user override
  - Requirement: MUST maintain 60 FPS
  - Requirement: MUST handle terminal resize gracefully

- **Message Display**: Rich formatting
  - User/Assistant/System/Reasoning messages
  - Markdown rendering with syntax highlighting
  - Spinner animations for long operations
  - Requirement: MUST support 256+ colors
  - Requirement: MUST handle emoji in messages

- **Input System**: Advanced text entry
  - Multiline input with text wrapping
  - Command history navigation
  - Completion popup with suggestions
  - Requirement: MUST support paste operations
  - Requirement: MUST handle very long inputs (10KB+)

- **Safety Controls**: User approval
  - Tool approval dialog before execution
  - Mode-based safety levels (ASK/NORMAL/PLAN)
  - Tool inspection and modification
  - Requirement: MUST block dangerous operations
  - Requirement: MUST provide clear risk information

- **Status Display**: Contextual information
  - Current working directory
  - Token usage
  - Mode indicator
  - Requirement: MUST update in real-time
  - Requirement: MUST not impact performance

### 2. Non-Functional Requirements

#### 2.1 Performance
- CLI startup time: < 1 second
- TUI startup time: < 2 seconds
- Tool execution latency: < 100ms per tool
- Requirement: MUST support streaming for long operations
- Requirement: MUST not block on I/O

#### 2.2 Reliability
- Session recovery: 100% on graceful shutdown
- Tool error handling: All errors caught and reported
- Agent resilience: Retries on transient failures
- Requirement: MUST have graceful degradation
- Requirement: MUST provide useful error messages

#### 2.3 Security
- Path traversal protection: No access outside working directory
- Command injection protection: Safe shell command building
- Sensitive data handling: No credentials in logs
- Requirement: MUST validate all file paths
- Requirement: MUST use subprocess safely

#### 2.4 Maintainability
- Code coverage: >80% for core modules
- Type safety: 100% mypy compliance
- Documentation: All public APIs documented
- Requirement: MUST follow PEP 8
- Requirement: MUST have integration tests

#### 2.5 Scalability
- Support codebases up to 100K files
- Handle projects with multi-GB file sizes
- Concurrent session support (testing)
- Requirement: MUST optimize for common patterns
- Requirement: MUST cache tool results where appropriate

### 3. Technical Constraints

#### 3.1 Dependencies
- Python 3.11+ (type hints, async/await features)
- Textual >= 1.0.0 (TUI framework)
- asyncclick >= 8.1 (async CLI)
- rich >= 13.0 (formatting)
- miu-core[anthropic] (agent framework)

#### 3.2 Architectural Constraints
- Single working directory per agent instance
- No multi-process architecture (simplicity)
- No persistent cache (session-based only)
- Standard output for CLI, Textual for TUI

#### 3.3 API Constraints
- ReAct agent limited to 20 iterations max
- Tool execution timeout: 600 seconds default
- Model context window: determined by provider
- Response streaming required for TUI responsiveness

### 4. Success Metrics

#### 4.1 Functional Success
- All tools functional and tested
- Both CLI and TUI modes working
- Session persistence verified
- Multi-model provider support confirmed

#### 4.2 Performance Success
- CLI responds in < 1 second
- TUI renders without blocking
- Grep/Glob complete < 2 seconds on 1000 files
- Streaming produces visible output within 1 second of query

#### 4.3 Quality Success
- Test coverage > 80%
- Zero mypy errors
- All documented examples work
- Zero critical security issues

#### 4.4 User Success
- Developers can use tool within 5 minutes
- Slash commands intuitive and discoverable
- TUI controls self-explanatory
- Error messages guide toward solutions

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Points                          │
│  miu (CLI)  │  miu-tui (TUI)  │  miu --acp (ACP)       │
└────────────┬────────────────┬──────────────────────────┘
             │                │
      ┌──────▼──────┐  ┌──────▼──────┐
      │  CLI Entry  │  │   TUI App   │
      │ (asyncclick)│  │ (Textual)   │
      └──────┬──────┘  └──────┬──────┘
             │                │
             └────────┬───────┘
                      │
              ┌───────▼────────┐
              │  CodingAgent   │
              │  (ReAct)       │
              └───────┬────────┘
                      │
        ┌─────────────┼──────────────┐
        │             │              │
    ┌───▼────┐  ┌────▼────┐  ┌─────▼────┐
    │ Tools  │  │ Memory  │  │ Provider │
    │Registry│  │(Session)│  │(LLM APIs)│
    └────────┘  └─────────┘  └──────────┘
```

## Release History

### v0.2.0 (Current)
- Phase 1A: Workspace setup with all tools
- Phase 2: Enhanced UX with TUI framework
- Phase 3: MCP/ACP protocol scaffolding
- Phase 4: Type safety (mypy compliance)

### v0.1.0
- Initial CLI implementation
- Basic tool set

### Planned Releases
- **v0.3**: Advanced modes (PLAN, ASK) with enhanced safety
- **v0.4**: Custom command framework
- **v1.0**: Stable API, production ready

## Dependencies & Licensing

All dependencies are open source with compatible licenses:
- **miu-core**: MIT (internal)
- **textual**: MIT
- **asyncclick**: BSD
- **rich**: MIT
- **prompt-toolkit**: BSD
- **anthropic**: MIT (optional)

## Development Roadmap

### Q1 2025
- Fix remaining type checking issues
- Enhance TUI with preference system
- Add custom command support

### Q2 2025
- MCP server implementation
- Memory optimization for large codebases
- Performance benchmarking

### Q3 2025
- Plugin system for custom tools
- Collaborative session support
- IDE integration packages

### Q4 2025
- v1.0 release candidate
- Production deployment guides
- Enterprise features

## Team & Responsibilities

**Maintained by**: miumono project team
**Primary Language**: Python 3.11+
**Issue Tracking**: GitHub Issues
**Documentation**: `/docs` folder

## Open Questions & Considerations

1. Should we support remote file systems (SSH, cloud)?
2. What's the memory limit for conversation history?
3. Should we implement caching for repeated queries?
4. How to handle workspace-wide config files (.miurc)?
5. Should TUI support themes/customization?

## Conclusion

miu-code v0.2 establishes a solid, extensible foundation for AI-assisted coding. The dual interface approach (CLI + TUI) serves different workflows, while the ReAct agent with session persistence provides reliable, contextual assistance. Future releases will focus on advanced features and ecosystem integration while maintaining the simplicity and security-first approach.
