# Miu Code TUI Design

Terminal User Interface design documentation for Miu Code, inspired by [mistral-vibe](https://github.com/mistralai/mistral-vibe).

## Design Philosophy

### Core Principles

1. **Responsive UI** - Never block the event loop; use workers for async operations
2. **Interruptible** - User can always interrupt agent execution (Escape key)
3. **Auto-scroll with override** - Follow new content unless user scrolls up
4. **Minimal chrome** - Focus on content, hide unnecessary UI elements
5. **Consistent theming** - Miu teal brand colors throughout

### Inspiration: mistral-vibe Pattern

Key patterns adopted from mistral-vibe:

- **Worker-based execution**: Agent runs in background worker, UI stays responsive
- **Widget hierarchy**: Proper container nesting with `width: 1fr` for flexible layouts
- **Resize handlers**: All widgets implement `on_resize()` for dynamic layouts
- **Anchor scrolling**: Use `anchor()` method during streaming for smooth scroll

## Architecture Overview

```mermaid
flowchart TB
    subgraph App["MiuCodeApp"]
        direction TB
        A[VerticalScroll #chat]
        B[Horizontal #loading-area]
        C[Static #bottom-app-container]
        D[Horizontal #bottom-bar]
    end

    subgraph ChatArea["Chat Area"]
        A --> WB[WelcomeBanner]
        A --> CL[ChatLog #messages]
    end

    subgraph LoadingArea["Loading Area"]
        B --> LS[LoadingSpinner]
        B --> MI[Mode Indicator]
    end

    subgraph BottomApp["Bottom App (Switchable)"]
        C --> IC[ChatInputContainer]
        C --> AA[ApprovalApp]
    end

    subgraph BottomBar["Bottom Bar"]
        D --> PD[Path Display]
        D --> SP[Spacer]
        D --> TD[Token Display]
    end
```

## Widget Hierarchy

```mermaid
classDiagram
    class MiuCodeApp {
        +CodingAgent _agent
        +bool _is_processing
        +bool _interrupt_requested
        +run_worker()
        +action_interrupt()
    }

    class ChatLog {
        +AssistantMessage _streaming_msg
        +add_user_message()
        +start_streaming()
        +append_streaming()
        +end_streaming()
        +on_resize()
    }

    class AssistantMessage {
        +Markdown _markdown
        +MarkdownStream _stream
        +append_content()
        +stop_stream()
        +on_resize()
    }

    class UserMessage {
        +str _content
        +on_resize()
    }

    class ChatInputContainer {
        +ChatInputBody _body
        +CompletionPopup _completion_popup
        +focus_input()
        +clear_input()
    }

    class LoadingSpinner {
        +bool is_loading
        +start()
        +stop()
        +on_resize()
    }

    MiuCodeApp --> ChatLog
    MiuCodeApp --> ChatInputContainer
    MiuCodeApp --> LoadingSpinner
    ChatLog --> AssistantMessage
    ChatLog --> UserMessage
```

## Component Details

### App Layout (app.py)

The main application structure:

| Component | ID | Purpose |
|-----------|-----|---------|
| VerticalScroll | `#chat` | Scrollable message area |
| WelcomeBanner | `#banner` | Logo and metadata |
| ChatLog | `#messages` | Message container with `layout: stream` |
| LoadingSpinner | `#loading-area-content` | Animated loading indicator |
| Static | `#mode-indicator` | Current mode display |
| ChatInputContainer | `#input-container` | User input with history |
| Horizontal | `#bottom-bar` | Path and token display |

### Message Widgets (messages.py)

```mermaid
flowchart LR
    subgraph AssistantMessage
        direction TB
        H[Horizontal container]
        H --> D["● dot"]
        H --> V[Vertical content<br/>width: 1fr]
        V --> M[Markdown<br/>width: 100%]
    end

    subgraph UserMessage
        direction TB
        H2[Horizontal container]
        H2 --> P["> " prompt]
        H2 --> C[Static content<br/>width: 1fr]
    end
```

Key pattern for responsive width:
```
Container (width: 100%)
  └─ Horizontal (width: 100%)
      ├─ Icon (width: auto)
      └─ Content (width: 1fr)  ← Flexible fill
          └─ Markdown (width: 100%)
```

### Chat Input System

```mermaid
flowchart TB
    subgraph ChatInputContainer
        CP[CompletionPopup]
        IB[Input Box]

        subgraph ChatInputBody
            TA[ChatTextArea]
            HM[HistoryManager]
        end
    end

    TA -->|text change| CP
    TA -->|up/down| HM
    TA -->|enter| Submit[Submitted Event]
```

Components:
- **ChatInputContainer**: Top-level container with border styling
- **ChatInputBody**: Manages input and history
- **ChatTextArea**: Textual TextArea with custom key handling
- **CompletionPopup**: Autocomplete suggestions (hidden by default)
- **HistoryManager**: Persistent command history

## Event Flow

### Message Submission

```mermaid
sequenceDiagram
    participant U as User
    participant IC as ChatInputContainer
    participant App as MiuCodeApp
    participant CL as ChatLog
    participant Agent as CodingAgent

    U->>IC: Type message + Enter
    IC->>App: Submitted event
    App->>IC: clear_input()

    alt Agent running
        App->>App: _interrupt_agent()
    end

    App->>App: run_worker(_handle_user_message)
    App->>CL: add_user_message()
    App->>CL: start_streaming()

    loop Stream events
        Agent->>App: TextDeltaEvent
        App->>CL: append_streaming(text)
        App->>App: call_after_refresh(anchor)
    end

    App->>CL: end_streaming()
    App->>IC: focus_input()
```

### Interrupt Flow

```mermaid
sequenceDiagram
    participant U as User
    participant App as MiuCodeApp
    participant CL as ChatLog

    U->>App: Press Escape
    App->>App: action_interrupt()

    alt Is processing
        App->>App: _interrupt_requested = True
        App->>CL: end_streaming()
        App->>CL: add_system_message("Interrupted")
    else Not processing
        App->>App: focus_input()
    end
```

## Theming System (theme.py)

### Brand Colors

```mermaid
flowchart LR
    subgraph Gradient["Miu Gradient"]
        G1["#76D7C4<br/>bright cyan"]
        G2["#48C9B0<br/>light teal"]
        G3["#1ABC9C<br/>primary teal"]
        G4["#16A085<br/>dark teal"]
        G5["#0E6655<br/>deep teal"]

        G1 --> G2 --> G3 --> G4 --> G5
    end
```

### Semantic Colors

| Role | Color | Hex |
|------|-------|-----|
| User | Blue | `#3498DB` |
| Assistant | Teal | `#1ABC9C` |
| System | Gray | `#7F8C8D` |
| Error | Red | `#E74C3C` |
| Thinking | Light Teal | `#48C9B0` |

### Color Utilities

```python
# Gradient animation color
color = get_gradient_color(progress)  # 0.0 to 1.0

# Color interpolation
color = interpolate_color("#1ABC9C", "#48C9B0", 0.5)
```

## Styling (app.tcss)

### Layout Structure

```css
/* Main chat area - scrollable */
#chat {
    height: 1fr;        /* Fill available space */
    scrollbar-gutter: stable;
}

/* Messages container - stream layout */
#messages {
    layout: stream;     /* Vertical flow */
    width: 100%;
    height: auto;
}

/* Input box - bordered */
#input-box {
    border-top: solid $foreground-muted;
    border-bottom: solid $foreground-muted;
}
```

### Border Style Variants

Mode-based input border colors:
- **Default**: `$foreground-muted` (gray)
- **ASK mode**: `#27AE60` (green) - safe mode
- **PLAN mode**: `#F39C12` (orange) - warning

## Key Bindings

| Key | Action | Context |
|-----|--------|---------|
| `Ctrl+C` | Quit | Always |
| `Ctrl+N` | New session | Always |
| `Ctrl+L` | Clear chat | Always |
| `Escape` | Interrupt / Focus input | Always |
| `Shift+Tab` | Cycle mode | Always |
| `Shift+Up` | Scroll chat up | Always |
| `Shift+Down` | Scroll chat down | Always |
| `Up/Down` | History navigation | In input |
| `Enter` | Submit | In input |

## Resize Handling

All widgets that display dynamic content implement `on_resize()`:

```python
def on_resize(self) -> None:
    """Refresh on resize to ensure proper layout."""
    self.refresh()
```

Widgets with resize handlers:
- `WelcomeBanner`
- `ChatLog`
- `AssistantMessage`
- `UserMessage`
- `ReasoningMessage`
- `LoadingSpinner`
- `ExpandingBorder`

## Streaming Best Practices

1. **Use workers for async operations**:
   ```python
   self.run_worker(self._handle_user_message(value), exclusive=False)
   ```

2. **Schedule scroll after refresh**:
   ```python
   self.call_after_refresh(self._anchor_if_scrollable)
   ```

3. **Check interrupt flag in loops**:
   ```python
   async for event in agent.run_stream(query):
       if self._interrupt_requested:
           break
   ```

4. **Proper widget container structure**:
   ```python
   with Horizontal(classes="container"):
       yield Static("●", classes="icon")  # width: auto
       with Vertical(classes="content"):  # width: 1fr
           yield Markdown("")             # width: 100%
   ```

## File Structure

```
miu_code/tui/
├── app.py              # Main application
├── app.tcss            # Stylesheet
├── theme.py            # Colors and gradients
└── widgets/
    ├── banner.py       # Welcome banner
    ├── chat.py         # ChatLog container
    ├── messages.py     # Message widgets
    ├── loading.py      # Loading spinner
    ├── spinner.py      # Spinner mixin
    ├── status.py       # Status bar
    ├── approval.py     # Tool approval dialog
    ├── tools.py        # Tool-related widgets
    └── chat_input/
        ├── container.py      # Input container
        ├── body.py          # Input body
        ├── text_area.py     # Custom TextArea
        ├── history.py       # History manager
        └── completion_popup.py  # Autocomplete
```
