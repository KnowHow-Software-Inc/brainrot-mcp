# Brainrot MCP - Project Specifications

## How to use this
Apply these specs when planning, building, or validating built work.
**IMPORTANT**: the `content` examples are illustrative of how a user would use Brainrot MCP and NOT architecture requirements.

## API Contract

### POST /api/contexts
Create or update a context entry.

**Request Body:**
```json
{
    "key": "auth-pattern",
    "content": "Use JWT with refresh tokens",
    "project": "myapp",  // Auto-populated from cwd if not provided
    "tags": ["architecture", "auth"]  // Optional in Phase 1, required by Phase 4
}
```

**Response (201 Created):**
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

### GET /api/contexts/{key}
Retrieve a specific context by key.

**Response (200 OK):**
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

**Response (404 Not Found):**
```json
{
    "error": "Context not found",
    "key": "missing-key"
}
```

### GET /api/contexts
List all contexts with optional tag filtering (Phase 4).

**Query Parameters:**
- `tag` (optional): Filter contexts by tag
- `project` (optional): Filter contexts by project

**Response (200 OK):**
```json
[
    {
        "key": "auth-pattern",
        "content": "Use JWT with refresh tokens",
        "project": "myapp",
        "tags": ["architecture", "auth"],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
]
```

### PUT /api/contexts/{key}
Update an existing context (Phase 4).

**Request Body:**
```json
{
    "content": "Updated content",
    "tags": ["architecture", "auth", "updated"]
}
```

**Response (200 OK):**
Same as POST response

## MCP Tool Signatures

### Phase 2 Tools (Basic)
```python
def store_context(key: str, content: str) -> bool:
    """Store a context with the given key and content."""
    pass

def get_context(key: str) -> str:
    """Retrieve context content by key. Returns empty string if not found."""
    pass
```

### Phase 5 Tools (Extended)
```python
def store_context(key: str, content: str, tags: List[str] = None) -> bool:
    """Store a context with the given key, content, and optional tags."""
    pass

def list_contexts(filter_by_tag: str = None) -> List[dict]:
    """List all contexts, optionally filtered by tag."""
    pass

def update_context(key: str, content: str) -> bool:
    """Update an existing context's content."""
    pass
```

## Project Detection Logic

Both backend and MCP server must use identical project detection:

```python
import os

def get_current_project() -> str:
    """Get the current project name from working directory."""
    return os.path.basename(os.getcwd())
```

## Configuration

### Environment Variables

**Backend (.env):**
```bash
PORT=8000
HOST=0.0.0.0
DATABASE_URL=sqlite:///./data/brainrot.db
```

**MCP Server (.env):**
```bash
BACKEND_URL=http://localhost:8000
```

### Claude Desktop Configuration

Location: `~/.config/claude/claude_desktop_config.json`

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

## Error Handling

### Standard Error Response Format
All API errors should follow this format:

```json
{
    "error": "Human-readable error message",
    "details": {
        "key": "context-key",
        "reason": "not_found|invalid_format|server_error"
    }
}
```

### HTTP Status Codes
- 200: Success (GET, PUT)
- 201: Created (POST)
- 400: Bad Request (invalid input)
- 404: Not Found (missing key)
- 500: Internal Server Error

## Database Schema

### contexts table
```sql
CREATE TABLE contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    content TEXT NOT NULL,
    project TEXT NOT NULL,
    tags TEXT,  -- JSON array stored as text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project, key)
);
```

### Indexes
```sql
CREATE INDEX idx_project ON contexts(project);
CREATE INDEX idx_project_key ON contexts(project, key);
```

## Testing Validation

### Phase 1-3 Validation
```bash
# Store a context
curl -X POST http://localhost:8000/api/contexts \
  -H "Content-Type: application/json" \
  -d '{"key": "auth-pattern", "content": "Use JWT"}'

# Retrieve it
curl http://localhost:8000/api/contexts/auth-pattern
```

### Phase 4-6 Validation
```bash
# Store with tags
curl -X POST http://localhost:8000/api/contexts \
  -H "Content-Type: application/json" \
  -d '{"key": "todo-1", "content": "Implement auth", "tags": ["todo", "backend"]}'

# List by tag
curl http://localhost:8000/api/contexts?tag=todo
```

## Notes

- All timestamps should be in ISO 8601 format with UTC timezone
- Project scoping is automatic based on working directory
- Keys are unique within a project (project + key = unique constraint)
- Tags are stored as JSON array in SQLite TEXT field for simplicity