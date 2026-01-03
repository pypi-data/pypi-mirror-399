# miu-code System Architecture

**Version:** 0.2.0
**Last Updated:** 2025-12-31

## Architecture Overview

miu-code is a **layered architecture** with clear separation of concerns. Each layer handles specific responsibilities while maintaining loose coupling and high cohesion.

```
┌──────────────────────────────────────────────────────┐
│           User Interface Layer                         │
│  ┌─────────────────────────┬──────────────────────┐  │
│  │   CLI (asyncclick)      │   TUI (Textual)      │  │
│  │  - One-shot queries     │ - Interactive chat   │  │
│  │  - REPL mode            │ - Streaming display  │  │
│  │  - ACP server           │ - Widgets            │  │
│  └─────────────────────────┴──────────────────────┘  │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│           Command Processing Layer                    │
│  - Command expansion (/cook, /commit, /plan)        │
│  - Query preprocessing                               │
│  - Response formatting                               │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│           Agent Layer (miu-core)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │        CodingAgent                           │   │
│  │  - ReAct reasoning (20 iterations max)       │   │
│  │  - Tool management                           │   │
│  │  - Streaming support                         │   │
│  │  - Session persistence                       │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
        ↓                       ↓                 ↓
┌──────────────────┐  ┌────────────────┐  ┌──────────────┐
│   Tool Layer     │  │  Memory Layer  │  │ Provider     │
│                  │  │                │  │ Abstraction  │
│ • Read           │  │ • Session      │  │              │
│ • Write          │  │   Storage      │  │ • Anthropic  │
│ • Edit           │  │ • History      │  │ • OpenAI     │
│ • Bash           │  │   Management   │  │ • Google     │
│ • Glob           │  └────────────────┘  └──────────────┘
│ • Grep           │
│ • Security       │
└──────────────────┘
```

## Layer Details

### 1. User Interface Layer

#### 1.1 CLI Interface (`cli/entry.py`)

**Technology:** asyncclick (async CLI framework)

**Features:**
- Argument parsing and validation
- Command routing
- Help text generation
- Error reporting

**Command Structure:**
```
miu [QUERY]              # One-shot execution
miu --model <provider>   # Model selection
miu --session <id>       # Session management
miu --acp                # ACP server mode
miu tui                  # Launch TUI (subcommand)
```

**Flow:**
```
User Input
    ↓
[asyncclick parser] → Argument validation
    ↓
[Query preprocessing] → Slash command expansion
    ↓
[CodingAgent execution] → Response generation
    ↓
[Output formatting] → Console display (Rich)
```

**Key Components:**
- `cli()` - Main command group
- `tui()` - TUI subcommand
- Model/session options passed to agent

#### 1.2 TUI Interface (`tui/app.py`)

**Technology:** Textual >= 1.0.0

**Architecture:**
```
MiuCodeApp (main application)
├── WelcomeBanner (#banner)
│   └── Welcome header with metadata
├── Container (#main)
│   └── ChatLog (#chat)
│       ├── WelcomeBanner (initial)
│       ├── UserMessage widgets
│       └── AssistantMessage widgets
├── Vertical (#input-container)
│   ├── LoadingSpinner (#loading)
│   └── Input (#input)
└── Footer (key bindings)
```

**Event Flow:**
```
User types message
    ↓
[on_input_submitted] → Parse input
    ↓
[add_user_message] → Display in chat
    ↓
[start_loading] → Show spinner
    ↓
[run_stream] → Stream events from agent
    ├─ TextDeltaEvent → append_streaming
    ├─ ToolExecutingEvent → add_tool_call
    └─ ToolResultEvent → add_tool_result
    ↓
[end_streaming] → Stop spinner
    ↓
[focus_input] → Re-enable input
```

**Key Bindings:**
- `Ctrl+C` - Quit
- `Ctrl+N` - New session
- `Ctrl+L` - Clear chat
- `Enter` - Submit message

**Widgets:**
- `WelcomeBanner` - Metadata display
- `ChatLog` - Message container
- `LoadingSpinner` - Progress indicator
- `Input` - Text entry with history

### 2. Command Processing Layer

#### 2.1 Slash Command System (`commands/`)

**Architecture:**
```
CommandExecutor (miu-core)
    ↓
Registry of Commands
    ├─ /cook (implement feature)
    ├─ /commit (create git commit)
    ├─ /plan (create implementation plan)
    └─ Extensible for custom commands

Each command is a markdown template with:
- Metadata (description, arguments)
- Prompt template
- Variable substitution ($ARGUMENTS)
```

**Processing:**
```
User input "/plan update docs"
    ↓
[CommandExecutor.execute] → Lookup /plan
    ↓
[Load plan.md template]
    ↓
[Replace $ARGUMENTS with "update docs"]
    ↓
[Return expanded prompt to agent]
```

### 3. Agent Layer

#### 3.1 CodingAgent (`agent/coding.py`)

**Architecture:**
```
CodingAgent
├── Provider (LLM abstraction)
│   ├── Anthropic
│   ├── OpenAI
│   └── Google
├── ToolRegistry (manages available tools)
├── ReActAgent (miu-core, reasoning loop)
└── SessionStorage (conversation memory)
```

**Key Methods:**
```python
class CodingAgent:
    def __init__(
        model: str,
        working_dir: str,
        session_id: str | None
    ) -> None:
        # Initialize provider and agent

    async def run(query: str) -> Response:
        # Single query execution
        # Persists session afterward

    async def run_stream(
        query: str
    ) -> AsyncIterator[StreamEvent]:
        # Streaming execution
        # Yields events for real-time display
```

**ReAct Loop (miu-core):**
```
1. [Thinking] Agent reasons about request
    ↓
2. [Tool Selection] Agent chooses relevant tool(s)
    ↓
3. [Tool Execution] Tool runs (e.g., read file)
    ↓
4. [Observation] Agent observes tool result
    ↓
5. Repeat 1-4 up to 20 iterations
    ↓
6. [Final Response] Generate response
```

**System Prompt:**
```
You are a helpful AI coding assistant. You can read, write, and edit files,
run shell commands, and search through codebases.

When helping with coding tasks:
1. First understand the request clearly
2. Use tools to explore the codebase if needed
3. Make minimal, focused changes
4. Verify your changes work when possible

Be concise and direct in your responses.
```

#### 3.2 Tool Registry

**Tools Available:**
1. **ReadTool** - File content access
2. **WriteTool** - File creation
3. **EditTool** - Precision editing
4. **BashTool** - Shell commands
5. **GlobTool** - Pattern matching
6. **GrepTool** - Content search

**Registration:**
```python
tools = ToolRegistry()
for tool in get_all_tools():
    tools.register(tool)
```

**Tool Interface (miu-core):**
```python
class Tool(ABC):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    def get_parameters(self) -> dict: ...

    async def execute(self, **kwargs) -> str: ...
```

### 4. Tool Layer

#### 4.1 File Operations

**ReadTool** (`tools/read.py`)
```
Input: path, encoding, offset, limit
Processing:
  1. Validate path (security check)
  2. Open file
  3. Read with offset/limit
  4. Return content
Output: file content as string
```

**WriteTool** (`tools/write.py`)
```
Input: path, content
Processing:
  1. Validate path
  2. Create directories if needed
  3. Atomic write operation
  4. Preserve permissions
Output: success/error
```

**EditTool** (`tools/edit.py`)
```
Input: path, old_string, new_string
Processing:
  1. Read file
  2. Find and validate old_string
  3. Replace with new_string
  4. Write back
Output: updated content
```

#### 4.2 Shell & File System

**BashTool** (`tools/bash.py`)
```
Input: command, timeout
Processing:
  1. Validate command
  2. Execute in subprocess
  3. Capture stdout/stderr
  4. Handle timeouts
Output: command output
```

**GlobTool** (`tools/glob.py`)
```
Input: pattern
Processing:
  1. Expand pattern (*, ?)
  2. Traverse directories
  3. Sort by modification time
Output: list of matching paths
```

**GrepTool** (`tools/grep.py`)
```
Input: pattern, files, context
Processing:
  1. Compile regex
  2. Search files
  3. Gather context lines
Output: matches with file/line info
```

#### 4.3 Security Module

**Path Validation** (`tools/security.py`)
```python
def validate_path(path: str, working_dir: str) -> bool:
    # Ensure path is within working_dir
    # Resolve symlinks
    # Prevent directory traversal attacks
    # Return True if valid
```

**Security Checks:**
1. No `../` or absolute paths outside working_dir
2. Symlink resolution
3. Normalized path comparison
4. Whitelist of allowed operations

### 5. Memory Layer

#### 5.1 Session Storage (`session/storage.py`)

**Format:** JSONLines (one JSON object per line)

**Schema:**
```json
{
  "role": "user|assistant|system",
  "content": string | array,
  "timestamp": ISO8601,
  "model": "provider:model-name"
}
```

**Operations:**
```python
class SessionStorage:
    def load() -> list[Message]:
        # Load conversation history

    def save(messages: list[Message]) -> None:
        # Persist conversation to disk
```

**Storage Location:**
```
.miu/sessions/
├── <session-id-1>.jsonl
├── <session-id-2>.jsonl
└── ...
```

#### 5.2 Message Format

**User Message:**
```json
{
  "role": "user",
  "content": "read main.py"
}
```

**Assistant Message:**
```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Here's the content..."
    },
    {
      "type": "tool_use",
      "id": "tool_123",
      "name": "ReadTool",
      "input": {"path": "main.py"}
    }
  ]
}
```

### 6. Provider Abstraction Layer

**Supported Providers:**

| Provider | Models | Format |
|----------|--------|--------|
| Anthropic | claude-opus-4, claude-sonnet-4, etc. | `anthropic:model-name` |
| OpenAI | gpt-4o, gpt-4-turbo, etc. | `openai:model-name` |
| Google | gemini-2.0-flash, etc. | `google:model-name` |

**Provider Selection:**
```python
# Default
agent = CodingAgent()  # Uses claude-sonnet-4-20250514

# Custom provider
agent = CodingAgent(model="openai:gpt-4o")
agent = CodingAgent(model="google:gemini-2.0-flash")
```

**Provider Abstraction (miu-core):**
```python
provider = create_provider(model)
# Returns provider-specific implementation
# Handles API calls, streaming, etc.
```

## Data Flow Diagrams

### One-Shot Execution Flow

```
User Input
    ↓
[CLI parse args]
    ↓
[Create CodingAgent]
    ↓
[Expand slash commands]
    ↓
[agent.run(query)]
    ├─ [ReAct Loop - up to 20 iterations]
    │  ├─ Tool selection
    │  ├─ Tool execution
    │  └─ Observation
    │
    └─ [Save session]
       ↓
[Format response with Rich]
    ↓
[Print to console]
```

### TUI Streaming Flow

```
User Input (Ctrl+Enter)
    ↓
[Clear input field]
    ↓
[Add to ChatLog]
    ↓
[Start loading spinner]
    ↓
[agent.run_stream(query)]
    ├─ TextDeltaEvent → append_streaming()
    │   └─ Call display_streaming()
    ├─ ToolExecutingEvent → add_tool_call()
    │   └─ Display tool execution
    ├─ ToolResultEvent → add_tool_result()
    │   └─ Display tool output
    └─ MessageStopEvent → end_streaming()
       ↓
[Stop spinner]
    ↓
[Save session]
    ↓
[Re-enable input]
```

### Session Persistence Flow

```
[Agent executes query]
    ↓
[Agent.memory populated with messages]
    ↓
[session.save(messages)]
    └─ Iterate messages
       └─ Serialize to JSON
       └─ Append to .jsonl file
            ↓
         .miu/sessions/<id>.jsonl
```

### New Session Load

```
[User provides session ID]
    ↓
[Create CodingAgent with session_id]
    ↓
[SessionStorage.load()]
    └─ Read .miu/sessions/<id>.jsonl
       └─ Parse JSON lines
       └─ Create message objects
            ↓
[Load into agent.memory]
    ↓
[Agent uses history for context]
```

## Communication Protocols

### ACP Server Mode

**Purpose:** Editor integration

**Protocol:** JSON-RPC over sockets

**API Endpoints:**
```
/query
  - Execute coding query
  - Return streaming response

/tools
  - List available tools
  - Return tool definitions

/session
  - Manage sessions
  - Get/set session state
```

## Scalability Considerations

### Current Limitations

1. **Single working directory** - One agent instance per CodingAgent
2. **Memory-based history** - Entire session in memory
3. **No caching** - Repeated queries re-execute
4. **Linear processing** - One query at a time per agent

### Future Improvements (v1.0+)

1. **Distributed agents** - Multiple agents per workspace
2. **Memory optimization** - Summarization of old messages
3. **Query caching** - Cache common queries
4. **Concurrent processing** - Handle multiple queries
5. **Vector store** - Semantic search over codebase

## Error Handling & Recovery

### Error Categories

1. **Tool Errors** - File not found, permission denied
2. **Agent Errors** - Max iterations exceeded
3. **Provider Errors** - API rate limits, network issues
4. **Security Errors** - Path traversal attempts

### Recovery Strategies

```python
# Retry on transient failures
async def run_with_retry(query: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await agent.run(query)
        except TransientError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise

# Graceful degradation
try:
    result = tool.execute(...)
except ToolError as e:
    # Log error
    # Return user-friendly message
    # Continue conversation
```

## Testing Architecture

### Unit Tests
- Test individual tools in isolation
- Mock file system and subprocess
- Security validation tests

### Integration Tests
- Test agent with real tools
- End-to-end flows
- Session persistence

### UI Tests
- Widget rendering
- Event handling
- Streaming display

## Performance Characteristics

| Operation | Target | Current |
|-----------|--------|---------|
| CLI startup | <1s | ~0.5s |
| TUI startup | <2s | ~1.5s |
| Tool execution | <100ms | ~50ms |
| Streaming latency | <1s | ~0.5s |
| Codebase scan (1K files) | <2s | ~1.5s |

## Security Architecture

### Path Validation
```
User input → validate_path() → resolve symlinks →
normalize path → compare with working_dir → allow/deny
```

### Command Safety
```
Shell command → escape args → use subprocess safely →
capture output → sanitize display
```

### Session Security
```
Session stored locally → no network transmission →
file permissions for privacy
```

## Future Architecture (v1.0+)

### Planned Components

1. **Plugin System** - Extend with custom tools/providers
2. **Memory Store** - Vector database for semantic search
3. **Multi-workspace** - Support multiple projects
4. **Collaborative Features** - Shared sessions
5. **Performance Cache** - Results caching
6. **Monitoring** - Metrics and logging

### Evolution Path

```
v0.2 (Current)
  ↓
v0.3 (Advanced modes)
  ↓
v0.4 (Custom commands)
  ↓
v1.0 (Stable API, plugins)
  ↓
v2.0 (Distributed, collaborative)
```
