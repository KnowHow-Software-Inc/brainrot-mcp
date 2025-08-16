# 🧠 Brainrot MCP

> **Never lose context in your AI coding sessions again**

Brainrot MCP is a Model Context Protocol (MCP) server that solves the critical problem of context loss between AI coding sessions. Store project decisions, TODOs, and architectural patterns once, then access them seamlessly across any MCP-compatible AI assistant.

## 🚀 Why Brainrot MCP?

Have you ever:
- ✅ Explained the same project architecture to Claude multiple times?
- ✅ Lost important TODOs between coding sessions?
- ✅ Wished you could share context between VS Code and Claude Desktop?
- ✅ Wanted persistent memory for your AI coding assistant?

**Brainrot MCP solves all of these problems.**

## ⚡ Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/KnowHow-Software-Inc/brainrot-mcp.git
cd brainrot-mcp

# Create virtual environment
uv venv
uv pip install -r backend/requirements.txt
uv pip install -r mcp_server/requirements.txt
```

### 2. Start the Backend
```bash
python backend/server.py
```

To run with vector search enabled, set ENABLE_VECTOR_SEARCH=true
```bash
ENABLE_VECTOR_SEARCH=true uv run python server.py
```
The API server will start on `http://localhost:8000`

### 3. Configure Claude Desktop
Add this to your `~/.config/claude/claude_desktop_config.json`:

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

### 4. Restart Claude Desktop
Restart Claude Desktop and you're ready to go! 🎉

## 💡 Usage Examples

### Store Architecture Decisions
```
push_context("auth-strategy", 
            "Using JWT with refresh tokens, 15min access token expiry, Redis for token storage", 
            tags=["architecture", "security"], 
            priority="high")
```

### Save Project TODOs
```
push_context("optimize-database",
            "Add database indexes for user queries - currently taking 2+ seconds", 
            tags=["todo", "performance", "backend"],
            priority="high")
```

### Retrieve Context Later
```
pop_context("auth-strategy")
# Returns: Architecture decision with smart instructions
# 📐 ARCHITECTURE DECISION: Apply this pattern consistently...

list_contexts(tag="performance")
# Lists all performance-related contexts with summaries
```

## 🛠️ Available MCP Tools

| Tool | Description | Example |
|------|-------------|---------|
| `push_context` | Store context with auto-summarization | Store coding patterns, decisions, TODOs |
| `pop_context` | Retrieve context with smart instructions | Get architecture decisions with usage guidance |
| `list_contexts` | List all contexts with filtering | Show all TODOs or security-related items |
| `delete_context` | Remove outdated context | Clean up completed TODOs |

### ✨ New Features
- **Auto-summarization**: Long content is automatically summarized for quick reference
- **Smart instructions**: Retrieved contexts include contextual guidance based on tags
- **Priority levels**: Mark TODOs and technical debt with priority (low/medium/high)
- **Metadata support**: Rich context information with timestamps and source tracking
- **Vector Search**: Semantic search to find related contexts even without exact keywords
- **Robust Tag Support**: Reliable tag filtering and categorization for better organization

## 🏗️ Architecture

```
brainrot-mcp/
├── backend/              # FastAPI server + SQLite database
├── mcp_server/          # MCP server implementation  
├── data/                # SQLite database storage
└── frontend/            # Optional web dashboard
```

**Flow**: MCP Client → MCP Server → HTTP API → SQLite Database

## 🎯 Real-World Examples

### Example 1: Multi-Session Project Development
**Day 1**: Store your database schema decisions
```
push_context("db-schema", 
            "Users table: id, email, password_hash. Posts table: id, user_id, content, created_at", 
            tags=["database", "schema"], 
            priority="high")
```

**Day 5**: Claude remembers your schema with smart instructions
```
pop_context("db-schema")
# Returns with instructions: "📌 STORED CONTEXT: Apply this information as appropriate..."
```

### Example 2: Team Coding Standards
```
push_context("error-handling", 
            "Always use custom AppError class with error codes. Log to structured JSON format", 
            tags=["standards", "errors", "pattern"],
            priority="medium")
```

### Example 3: Performance Tracking with Priorities
```
push_context("slow-query-fix", 
            "User dashboard query optimized from 3s to 200ms using compound index on (user_id, created_at)", 
            tags=["performance", "solved"],
            priority="low")  # Low priority since it's already solved
```

## 🚦 Development

### Running Tests
```bash
# Backend tests
cd backend && pytest tests/

# Test MCP server
npx @modelcontextprotocol/inspector uv run python mcp_server/server.py
```

### Code Quality
```bash
# Linting
ruff check .

# Type checking  
mypy .
```

## 📋 Requirements

- **Python 3.11+**
- **uv** (recommended) or pip
- **Claude Desktop** or other MCP-compatible client
- **FastMCP framework** (automatically installed)
- **SQLite** (included with Python)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the linting and tests
6. Submit a pull request

## 📖 How It Works

1. **Push Context**: Use `push_context()` to save any project information with auto-summarization
2. **Automatic Persistence**: Everything saves to a local SQLite database with metadata
3. **Smart Retrieval**: `pop_context()` returns content with contextual instructions
4. **Cross-Session Memory**: Context persists across all your AI coding sessions
5. **Intelligent Filtering**: Use tags and priorities to organize and find relevant context

## 🔧 Troubleshooting

**MCP server not connecting?**
- Check that the backend is running on port 8000
- Verify the path in your Claude Desktop config
- Restart Claude Desktop after config changes

**Database issues?**
- The SQLite database auto-creates at `data/brainrot.db`
- Check file permissions in the `data/` directory

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🎊 What's Next?

- [ ] Multi-project support with namespacing
- [ ] Team collaboration features and shared contexts
- [ ] Enhanced AI-powered context suggestions and insights
- [ ] Export/import functionality for context sharing
- [ ] VS Code extension for direct integration
- [ ] Context relationships and linking
- [ ] Full-text search across all stored contexts

---

**Made with ❤️ for developers who are tired of explaining the same thing to AI assistants over and over again.**

*Star ⭐ this repo if Brainrot MCP saves you time!*