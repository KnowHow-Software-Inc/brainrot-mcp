# Brainrot MCP - Technical Stack

## Purpose
Enable persistent context management across AI coding sessions as defined in the PRD.

## Core Components

### Backend API
- **FastAPI**: REST API for context storage and retrieval
- **SQLite**: File-based database for context persistence
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization

### MCP Server
- **MCP Library**: Protocol implementation for AI assistant integration
- **Requests**: HTTP client to communicate with backend API

### Configuration
- **python-dotenv**: Environment variable management

## Data Model
```json
{
  "key": "auth-pattern",
  "content": "Use JWT with refresh tokens",
  "project": "myapp",
  "tags": ["architecture", "auth"],
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

## API Endpoints
- `POST /api/contexts` - Store context
- `GET /api/contexts/{key}` - Retrieve context
- `GET /api/contexts` - List contexts (with tag filtering)
- `PUT /api/contexts/{key}` - Update context
- `DELETE /api/contexts/{key}` - Delete context

## MCP Tools
- `store_context(key, content, tags)` - Save context with tags
- `get_context(key)` - Retrieve by key
- `list_contexts(filter_by_tag)` - List all or filter by tag
- `update_context(key, content)` - Update existing context
- `delete_context(key)` - Remove context

## Dependencies

### Backend
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-dotenv==1.0.0
```

### MCP Server
```
mcp==1.0.0
requests==2.31.0
python-dotenv==1.0.0
```

## Key Design Choices

1. **SQLite**: Simple, file-based storage perfect for single-user context management
2. **FastAPI**: Modern async framework with automatic API documentation
3. **MCP Protocol**: Native integration with AI coding assistants
4. **Flat key-value store**: Simple retrieval without complex hierarchies
5. **Tag-based organization**: Flexible categorization without rigid structure

These choices directly support the PRD goals of cross-IDE context sharing and persistent knowledge management without unnecessary complexity.