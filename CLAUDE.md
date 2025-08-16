# Brainrot MCP - Project Context

## 🎯 Project Vision

Brainrot MCP is a Model Context Protocol (MCP) server that solves the critical problem of context loss between AI coding sessions. It enables developers to capture, store, and retrieve project context seamlessly within AI coding assistants like Claude Code, VS Code, and other MCP-compatible tools.

## 🚀 Core Value Proposition

An MCP server that seamlessly captures, stores, and retrieves project context within AI coding sessions, enabling:
- **Persistent Knowledge**: Never lose valuable project decisions between sessions
- **Cross-IDE Context Sharing**: Store context in Claude Code, retrieve in VS Code
- **Architecture Consistency**: Maintain consistent patterns across your entire codebase
- **Long-Running Project Management**: Track TODOs, technical debt, and goals across sessions

## 🏗️ Architecture Overview

```
brainrot-mcp/
├── backend/              # FastAPI backend server
│   ├── server.py        # Main API server
│   ├── database.py      # SQLite database management
│   └── models.py        # Pydantic data models
├── mcp_server/          # MCP server implementation
│   ├── server.py        # FastMCP server with context tools
│   ├── tools/           # MCP tool implementations
│   └── resources/       # MCP resource providers
├── frontend/            # Web dashboard (optional)
│   └── index.html       # Single-page context viewer
└── data/                # SQLite database storage
    └── brainrot.db      # Context storage database
```

## 🛠️ Key Features

### Phase 1: Core Context Management (MVP)
- `store_context(key, content, metadata)` - Store any context with tags/categories
- `get_context(key)` - Retrieve specific context by key
- `list_contexts(filter_by_tag)` - List all contexts with optional filtering
- `update_context(key, content)` - Update existing context
- `delete_context(key)` - Remove context when no longer needed

### Phase 2: Enhanced Features
- **Context Categories**: Architecture decisions, TODOs, tech debt, patterns
- **Metadata Support**: Tags, timestamps, priority levels
- **Search Capabilities**: Full-text search across all stored contexts
- **Export/Import**: Share contexts between projects or team members

### Phase 3: Advanced Capabilities
- **Cross-Model Collaboration**: Export contexts for use with GPT/Gemini
- **Context Validation**: AI-powered validation against stored patterns
- **Background Analysis**: Queue contexts for async AI processing
- **Context Relationships**: Link related contexts together

## 📦 Technical Stack

### Backend Components
- **FastAPI**: High-performance async API server
- **SQLite**: Lightweight, file-based database for context storage
- **Pydantic**: Data validation and serialization
- **aiosqlite**: Async SQLite operations

### MCP Server
- **FastMCP**: Simplified MCP server implementation
- **httpx**: Async HTTP client for backend communication
- **python-dotenv**: Environment configuration management

## 🎮 Usage Examples

### Store Architecture Decision
```python
# In Claude Code or any MCP client
await store_context(
    key="auth-pattern",
    content="Use JWT with refresh tokens, 15min access token expiry",
    metadata={
        "tags": ["architecture", "security"],
        "priority": "high"
    }
)
```

### Track Technical Debt
```python
await store_context(
    key="tech-debt-validation",
    content="Input validation is inconsistent across endpoints",
    metadata={
        "tags": ["tech-debt", "backend"],
        "priority": "medium"
    }
)
```

### Retrieve Context in New Session
```python
# Days later, in a different session
auth_context = await get_context("auth-pattern")
# Returns: "Use JWT with refresh tokens, 15min access token expiry"

# List all technical debt
debt_items = await list_contexts(filter_by_tag="tech-debt")
```

## 🚦 Quick Start

### 1. Backend Setup
```bash
cd backend
uv venv
uv pip install fastapi uvicorn aiosqlite python-dotenv
uv run python server.py
```

### 2. MCP Server Setup
```bash
cd mcp_server
uv venv
uv pip install fastmcp httpx python-dotenv
```

### 3. Configure Claude Desktop
Add to `~/.config/claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "brainrot": {
      "command": "uv",
      "args": ["run", "python", "/path/to/brainrot-mcp/mcp_server/server.py"],
      "env": {
        "BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

## 🎯 Success Metrics

- **Response Time**: < 2 seconds for store/retrieve operations
- **Context Types**: Support code snippets, decisions, requirements, TODOs
- **Cross-Session**: Seamless context availability across different AI sessions
- **Zero Context Loss**: All stored contexts persist between sessions

## 🔧 Development Commands

### Testing
```bash
# Run backend tests
cd backend && pytest tests/

# Test MCP server with inspector
npx @modelcontextprotocol/inspector uv run python mcp_server/server.py
```

### Linting & Type Checking
```bash
# Run linting
ruff check .

# Type checking
mypy .
```

## 📝 Implementation Notes

### Database Schema
The SQLite database uses a simple key-value store with metadata:
- **contexts** table: id, key, content, metadata (JSON), created_at, updated_at
- **tags** table: id, context_id, tag_name (for efficient filtering)

### API Endpoints
- `POST /api/contexts` - Create new context
- `GET /api/contexts/{key}` - Retrieve specific context
- `GET /api/contexts` - List all contexts (with filtering)
- `PUT /api/contexts/{key}` - Update existing context
- `DELETE /api/contexts/{key}` - Delete context

### MCP Tools
All MCP tools communicate with the backend API to ensure data consistency:
- Tools handle authentication and request formatting
- Backend manages persistence and validation
- Responses are formatted for optimal LLM consumption

## 🚀 Future Enhancements

1. **Multi-Project Support**: Namespace contexts by project
2. **Team Collaboration**: Share contexts across team members
3. **Context Versioning**: Track changes to contexts over time
4. **AI-Powered Insights**: Analyze stored contexts for patterns
5. **Integration Webhooks**: Notify external systems of context changes

## 🤝 Contributing

When adding new features:
1. Follow the existing modular architecture
2. Add appropriate type hints and documentation
3. Include tests for new functionality
4. Update this CLAUDE.md with significant changes

## 📖 Key Design Decisions

1. **SQLite over PostgreSQL**: Simplicity and portability for individual developers
2. **FastAPI over Flask**: Better async support and automatic API documentation
3. **Flat key-value store**: Simplicity over hierarchical organization
4. **Tags over folders**: More flexible organization without rigid structure
5. **MCP over direct API**: Seamless integration with AI assistants

---

This project enables developers to maintain continuous context across AI coding sessions, eliminating the repetitive explanations and ensuring consistent architectural decisions throughout the development lifecycle.