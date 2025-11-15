# Kortix/Suna Codebase Architecture

## Project Overview

Kortix is an open-source platform for building, managing, and training AI agents. It includes **Suna**, a flagship generalist AI worker agent that demonstrates the platform's capabilities. The codebase consists of four main components working together: a Python/FastAPI backend, a Next.js frontend, isolated Docker execution sandboxes, and a Supabase-powered database layer.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js/React)                 │
│  - Agent Dashboard & Management UI                              │
│  - Chat Interfaces for agent interactions                        │
│  - Agent Configuration & Builder                                │
│  - Real-time monitoring & status updates                        │
└────────────────────────────┬──────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
┌───────────────▼──────────────┐ ┌─────────────────────────────────┐
│   Backend API (FastAPI)      │ │  Supabase (Auth + Database)     │
│                              │ │                                 │
│  - Thread Management         │ │  - User authentication          │
│  - Agent Orchestration       │ │  - Agent configurations         │
│  - AgentPress Framework      │ │  - Conversation history         │
│  - Tool System & Registry    │ │  - File storage                 │
│  - Billing & Credits         │ │  - Real-time subscriptions      │
│  - LLM Integration (Claude)  │ │  - Analytics                    │
│  - MCP & Composio Support    │ │                                 │
│  - Webhook handlers          │ │                                 │
└─────────────┬────────────────┘ └─────────────────────────────────┘
              │
┌─────────────▼─────────────────────────────────────────────────┐
│        Agent Runtime (Docker Sandboxes via Daytona)           │
│                                                                │
│  Per-agent isolated Linux environments with:                  │
│  - Chrome browser for web automation                          │
│  - VNC server for visual interaction                          │
│  - Web server (port 8080) for serving content                │
│  - Full file system access & sudo privileges                 │
│  - Supervisord for process management                        │
│  - Code execution capability                                 │
└────────────────────────────────────────────────────────────┘
```

## Backend Architecture Details

### 1. AgentPress Framework (`backend/core/agentpress/`)

The **AgentPress** framework is the core orchestration engine for agent execution. It manages the LLM interaction loop, tool calling, and conversation state.

**Key Components:**

- **ThreadManager** (`thread_manager.py` - 693 lines)
  - Manages conversation threads (containers for messages)
  - Handles LLM API calls with streaming and non-streaming responses
  - Implements auto-continue logic (automatic follow-up calls when LLM reaches length limits)
  - Manages message persistence to Supabase
  - Handles billing and token counting
  - Central orchestrator for the entire execution flow

- **ResponseProcessor** (`response_processor.py` - 2096 lines)
  - Processes LLM responses (streaming and non-streaming)
  - Detects and parses XML-based tool calls (`<tool>...</tool>` format)
  - Detects and parses native function calls (OpenAI-style format)
  - Orchestrates tool execution (sequential or parallel)
  - Manages tool result formatting and callback handling
  - Implements `ProcessorConfig` for flexible tool execution strategies

- **Tool System** (`tool.py`, `tool_registry.py`)
  - Base `Tool` abstract class for all tool implementations
  - `ToolRegistry` for managing and accessing tools
  - OpenAPI schema support for native function calling
  - Tool metadata (display names, icons, visibility)
  - Method metadata for individual tool functions
  - `ToolResult` container for standardized outputs

- **XMLToolParser** (`xml_tool_parser.py`)
  - Parses XML-based tool calls from LLM responses
  - Handles malformed XML gracefully
  - Supports inline tool results editing

- **Context Manager** (`context_manager.py` - 957 lines)
  - Implements context window optimization
  - Compresses conversation history when approaching token limits
  - Smart thresholding based on model's context window size
  - Preserves message importance while reducing tokens

- **Prompt Caching** (`prompt_caching.py` - 704 lines)
  - Implements Anthropic's prompt caching for cost reduction
  - Strategic caching of system prompts and conversation blocks
  - Cache invalidation and rebuilding logic
  - Token usage tracking for cached blocks

- **Error Processor** (`error_processor.py`)
  - Standardized error handling and categorization
  - Graceful degradation for API failures
  - Langfuse integration for error tracking

### 2. Agent Management System

**Agent Definition & Configuration:**

Agents are defined through a hierarchical configuration system:

- **Agents Table (Supabase)**
  - `agent_id`: Unique identifier
  - `name`, `description`: Display information
  - `account_id`: Owner (for multi-tenancy)
  - `is_default`: Whether it's the default agent for user
  - `is_public`: Public sharing capability
  - `tags`, `icon_*`: UI customization
  - `current_version_id`: Points to active configuration

- **Agent Versions Table**
  - `system_prompt`: LLM instruction
  - `model`: LLM model ID (e.g., "gpt-5", "claude-3-opus")
  - `configured_mcps`: List of enabled MCP servers
  - `custom_mcps`: User-added MCP configurations
  - `agentpress_tools`: Enabled AgentPress tools with config
  - `triggers`: Event-based automation rules

**Key Files:**

- `agent_loader.py` - Unified agent data loading and transformation
  - `AgentData` dataclass as single source of truth
  - Configuration merging (from version or fallback)
  - Version history tracking

- `agent_crud.py` - Create, Read, Update, Delete operations
- `agent_service.py` - Higher-level agent logic (filtering, pagination)
- `agent_runs.py` - Agent execution management and streaming
- `agent_setup.py` - Initial setup and configuration
- `agent_tools.py` - Agent tool configuration API

### 3. Thread & Conversation Management

**Threads Table (Supabase):**
- `thread_id`: Unique conversation identifier
- `account_id`: Owner
- `project_id`: Optional grouping
- `is_public`: Shareable conversations
- `metadata`: Cache flags, compression state

**Messages Table:**
- `message_id`: Unique message identifier
- `thread_id`: Parent thread
- `type`: "user", "assistant", "tool_call", "tool_result", "llm_response_end", etc.
- `content`: Message body (JSON or text)
- `is_llm_message`: Whether to include in context
- `metadata`: Compression flags, tool info

**Auto-Continue Logic:**
- When LLM hits length limits, ThreadManager automatically calls it again
- Accumulates partial content across iterations
- Respects max iteration limits (default 25)
- Triggered by `finish_reason == 'length'` or `finish_reason == 'tool_calls'`

### 4. Tool System Architecture

**Tool Execution Flow:**

```
LLM Response
    ↓
[XML Parser] ← Parses <tool>...</tool> tags
    ↓
[Native Parser] ← Parses function_calls array
    ↓
[Tool Registry] ← Looks up tool implementations
    ↓
[Tool Executor] ← Calls tool methods with arguments
    ↓
[Tool Results] ← Formatted and added back to conversation
    ↓
[Auto-Continue] ← Triggers another LLM call if needed
```

**Tool Types:**

1. **AgentPress Tools** (`backend/core/tools/`)
   - `SandboxFilesTool` - File operations in sandbox
   - `SandboxShellTool` - Command execution
   - `SandboxBrowserTool` - Web automation
   - `SandboxVisionTool` - Image analysis
   - `SandboxDesignerTool` - Design editing
   - `AgentCreationTool` - Nested agent creation
   - Custom user-created tools

2. **MCP Tools** (Model Context Protocol)
   - Dynamic tools from MCP servers
   - Configured per-agent
   - Integration with Composio
   - Custom MCP server support

3. **Composio Tools**
   - Pre-built integrations with 500+ services
   - OAuth-based authentication
   - Trigger support for automation

### 5. LLM Integration

**Multi-Model Support via LiteLLM:**

- **Primary Models**
  - Anthropic Claude (Claude 3 Opus, Sonnet, Haiku)
  - OpenAI (GPT-4, GPT-5)
  - Open-source models via OpenRouter
  - Deepseek, Groq, and other providers

- **Model Manager** (`ai_models/manager.py`)
  - Model registry with capabilities and pricing
  - Cost calculation per token
  - Context window awareness
  - Fallback handling

- **LLM Service** (`services/llm.py`)
  - Unified API call interface
  - Streaming support
  - Error handling and retries
  - Provider fallback (e.g., to OpenRouter on Anthropic overload)

### 6. Billing & Credits System

**Integration Points:**

- **ThreadManager** calls billing after each LLM response
- **Token Tracking**
  - Prompt tokens (including cache reads)
  - Completion tokens
  - Cache creation tokens
  - Cache read tokens

- **Cost Calculation**
  - Per-model pricing configuration
  - Prompt caching discounts (90% reduction on cache hits)
  - Free tier limits
  - Credit deduction on message completion

**Credit Types:**
- Standard credits (usage-based)
- Subscription quotas (monthly allocation)
- Trial credits (new users)

### 7. Database Layer (Supabase)

**Key Tables:**

1. **Users & Auth**
   - `auth.users` (Supabase Auth)
   - `profiles` (user metadata)
   - `subscriptions` (billing tier)

2. **Agents**
   - `agents` - Agent definitions
   - `agent_versions` - Configuration history
   - `agent_templates` - Shareable templates

3. **Execution**
   - `threads` - Conversations
   - `messages` - Individual messages
   - `agent_runs` - Execution records

4. **Tools & Integration**
   - `mcp_connections` - MCP server configs
   - `composio_connections` - Composio integrations
   - `credentials` (encrypted) - API keys, tokens

5. **Files & Content**
   - `files` - User-uploaded files
   - `knowledge_bases` - File collections

**Real-time Features:**
- PostgreSQL subscriptions for live updates
- Webhook support for external integrations
- File triggers for automation

### 8. Sandbox & Execution Environment

**Daytona Integration** (`sandbox/sandbox.py`):

- Creates isolated Docker containers per agent
- Environment: Ubuntu Linux with development tools
- **Pre-installed Services:**
  - Chrome/Chromium for browser automation
  - VNC server (port 5900) for visual access
  - Web server (port 8080) for serving files
  - Supervisord for process supervision
  - Python, Node.js, Git, and standard utilities

- **Lifecycle:**
  - `create_sandbox()` - Spin up new container
  - `get_or_start_sandbox()` - Resume archived containers
  - Snapshots for fast initialization
  - Labeled for identification

**Tool-Sandbox Communication:**
- Tools execute commands via Daytona's process API
- File system access to `/workspace` directory
- Session-based command execution
- Support for long-running processes

### 9. MCP (Model Context Protocol) & Composio

**MCP Module** (`mcp_module/mcp_service.py`):

- Connects to MCP servers (stdio, SSE, HTTP)
- Dynamic tool discovery from servers
- Secure credential management
- Session lifecycle management
- Error handling and reconnection logic

**Composio Integration** (`composio_integration/`):

- OAuth authentication for 500+ services
- Toolkit integration (Google, Slack, Zendesk, etc.)
- Auth config and connection management
- MCP server wrapping for Composio tools
- Profile management for multi-account support

**Integration Architecture:**
```
Agent → AgentPress → Tool Registry
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
    AgentPress Tools   MCP Servers
                          ↓
                   Composio Toolkit
                   (Google, Slack, etc.)
```

## Frontend Architecture

**Next.js-based application** (`frontend/src/`):

- **App Structure** (`app/`)
  - Route-based pages and layouts
  - API route handling
  - Server and client components

- **Components** (`components/`)
  - UI components for agent management
  - Chat interface
  - File uploads
  - Settings panels
  - Workflow builders

- **Hooks** (`hooks/`)
  - Custom React hooks for state management
  - API integration
  - Real-time subscriptions to Supabase

- **Stores** (`stores/`)
  - State management (likely Zustand or Redux)
  - Agent configuration state
  - User preferences
  - Conversation history

- **Environment Config:**
  - Supabase URL and keys (public)
  - Backend API URL
  - Environment mode (LOCAL, STAGING, PRODUCTION)

## Key Architectural Patterns

### 1. Conversation Threading Model

Every agent interaction happens within a **thread** context:

```python
# Create thread
thread_id = await thread_manager.create_thread(account_id)

# Add user message
await thread_manager.add_message(thread_id, "user", user_input)

# Run the thread (LLM + tools + auto-continue)
response_stream = await thread_manager.run_thread(
    thread_id=thread_id,
    system_prompt=agent_config['system_prompt'],
    llm_model='gpt-5',
    stream=True
)

# Stream responses to client
async for chunk in response_stream:
    yield chunk
```

### 2. Tool Registration & Execution

**Pattern: Decorator-based Tool Definition**

```python
@tool_metadata(
    display_name="File Operations",
    description="Create, read, edit files",
    weight=20,
    visible=True
)
class SandboxFilesTool(Tool):
    @method_metadata(display_name="Create File")
    @openapi_schema({...})
    async def create_file(self, path: str, content: str) -> ToolResult:
        # Implementation
        return self.success_response({"created": path})
```

**Registration:**
```python
thread_manager.add_tool(SandboxFilesTool)
```

**Execution:**
- ThreadManager detects tool calls in LLM response
- Looks up tool in ToolRegistry
- Invokes method with LLM-provided arguments
- Formats result and adds to conversation

### 3. Streaming Response Pipeline

**Streaming Architecture:**

```
LLM Streaming → Response Processor → Message Formatting → Client WebSocket
   ↓
Tool Detection (XML/Native)
   ↓
Tool Execution
   ↓
Tool Result Addition
   ↓
Status Updates
   ↓
Completion Handling
```

**Message Types Streamed:**
- `"content"` - Text content chunks
- `"tool_call"` - Tool invocation started
- `"tool_result"` - Tool result received
- `"status"` - Execution status updates
- `"error"` - Error messages

### 4. Agent Configuration as Code

Agents are versioned configurations:

```python
config = {
    'system_prompt': '...',           # LLM instruction
    'model': 'gpt-5',                 # Model selection
    'configured_mcps': ['google'],    # MCP servers
    'custom_mcps': [...],             # Custom configs
    'agentpress_tools': {             # Enabled tools
        'SandboxFilesTool': {
            'enabled': True,
            'functions': ['create_file', 'read_file']
        },
        'SandboxBrowserTool': {
            'enabled': True
        }
    },
    'triggers': [...]                 # Automation rules
}
```

### 5. Prompt Caching & Context Optimization

**Three-Layer Optimization:**

1. **Prompt Caching** (Anthropic feature)
   - Caches system prompt and conversation blocks
   - 90% token cost reduction on cache hits
   - Strategic cache invalidation

2. **Context Compression**
   - Summarizes old messages when approaching limits
   - Preserves important information
   - Triggered by token counting

3. **Message Truncation**
   - Loads messages in batches (1000 at a time)
   - Compressed content replaces full content for old messages
   - Metadata flags track compression state

## Testing Strategy

**Test Organization:**
- Files end with `.test.py` in `tests/` directories
- Pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.llm`
- Test runner: `./test` script or `uv run pytest`

**Test Types:**
- **Unit Tests** (fast, no external dependencies)
- **Integration Tests** (require database/services)
- **LLM Tests** (real API calls, cost money)

**Running Tests:**
```bash
./test --unit              # Run only unit tests
./test --integration       # Run integration tests
./test --coverage          # Generate coverage report
./test --path core/services  # Run tests in specific path
```

## Important Integrations

### External Services

1. **Supabase**
   - PostgreSQL database
   - Authentication (JWT)
   - Real-time subscriptions
   - File storage (S3-compatible)
   - Vector search for embeddings

2. **Composio**
   - 500+ service integrations
   - OAuth token management
   - Workflow automation
   - Trigger system

3. **Daytona**
   - Managed Docker execution
   - Sandbox provisioning
   - Session management
   - Snapshot-based initialization

4. **E2B** (if configured)
   - Alternative sandbox provider
   - Similar capabilities to Daytona

5. **LiteLLM**
   - Multi-provider LLM abstraction
   - Unified API across Claude, GPT, etc.
   - Automatic retries and fallbacks
   - Token counting utilities

6. **Langfuse**
   - LLM observability
   - Trace tracking
   - Performance monitoring
   - Cost analysis

## Development Workflow

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/kortix-ai/suna.git
cd suna

# 2. Run setup wizard (interactive configuration)
python setup.py

# 3. Start backend
cd backend
uv sync                    # Install dependencies
docker compose up redis    # Start Redis cache
uv run dramatiq run_agent_background --processes 4 --threads 4
uv run api.py             # Start FastAPI server (port 8000)

# 4. Start frontend
cd frontend
npm install
npm run dev               # Dev server (port 3000)
```

### Key Configuration Files

- `.env` / `.env.local` - Environment variables
- `backend/core/utils/config.py` - Centralized config management
- `backend/core/ai_models/registry.py` - Model definitions and pricing
- `docker-compose.yaml` - Service dependencies

### Common Development Tasks

**Adding a New Tool:**
1. Create class inheriting from `Tool` in `backend/core/tools/`
2. Use `@tool_metadata()` and `@openapi_schema()` decorators
3. Implement tool methods
4. Register with `thread_manager.add_tool()`

**Adding a New MCP Integration:**
1. Configure in agent's `configured_mcps`
2. MCP service handles connection and tool discovery
3. Tools automatically available in AgentPress

**Modifying Agent Behavior:**
1. Update system prompt in agent version
2. Enable/disable tools in config
3. Adjust model parameters (temperature, max_tokens)
4. Create new version for versioning

## Key Files Reference

| Path | Purpose | Lines |
|------|---------|-------|
| `backend/core/agentpress/thread_manager.py` | Core execution orchestrator | 693 |
| `backend/core/agentpress/response_processor.py` | Response parsing & tool execution | 2096 |
| `backend/core/agentpress/context_manager.py` | Context optimization | 957 |
| `backend/core/agentpress/prompt_caching.py` | Anthropic caching strategy | 704 |
| `backend/core/agent_loader.py` | Agent data loading | ~200 |
| `backend/core/agent_runs.py` | Execution endpoint | ~600 |
| `backend/core/sandbox/sandbox.py` | Daytona integration | ~300 |
| `backend/core/mcp_module/mcp_service.py` | MCP protocol handling | ~500 |
| `backend/core/composio_integration/composio_service.py` | Composio integration | ~200 |
| `backend/core/services/llm.py` | LiteLLM wrapper | ~300 |
| `backend/core/billing/billing_integration.py` | Credit management | ~400 |

## Common Debugging Patterns

### 1. Tool Not Executing
- Check if tool is registered in agent config
- Verify tool class is instantiated in tool registry
- Check OpenAPI schema format
- Look for errors in response processor logs

### 2. Context Window Issues
- Enable context manager to auto-compress
- Check `ENABLE_CONTEXT_MANAGER` flag in thread_manager.py:318
- Monitor token counts in logs
- Adjust model based on context needs

### 3. Billing Issues
- Check deduct_usage logs in thread_manager.py:121+
- Verify token counting matches LLM usage
- Look for cache hit statistics in logs
- Check model pricing in ai_models/registry.py

### 4. Sandbox Issues
- Check Daytona connection in sandbox.py logs
- Verify snapshot name matches configuration
- Check environment variables passed to container
- Look for supervisord startup logs

## Performance Considerations

1. **Token Optimization**
   - Prompt caching reduces costs 90%
   - Context compression handles long conversations
   - Fast path token checking avoids recalculation

2. **Concurrency**
   - ThreadManager is async throughout
   - Multiple threads execute independently
   - Tools can execute in parallel (configurable)

3. **Caching**
   - Redis for session cache
   - Supabase connection pooling
   - Message batch loading (1000 at a time)

4. **Streaming**
   - Streaming responses reduce perceived latency
   - Chunks streamed immediately to client
   - Tool execution can happen during stream

## Future Architecture Notes

- MCP becomes increasingly important for tool flexibility
- Composio provides 500+ integrations without custom coding
- Sandbox execution provides isolation and security
- Prompt caching will become standard for cost optimization
- Context compression handles growing conversation lengths

---

**Last Updated:** November 2025
**Project:** Kortix (formerly Suna)
**Repository:** https://github.com/kortix-ai/suna
