# Brainrot MCP Setup Guide

Complete setup instructions for the Brainrot MCP server - a context management system for AI coding sessions.

## 📋 Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- Claude Desktop app (for MCP integration)

### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd brainrot-mcp
```

### 2. Backend Server Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with uv
uv venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Start the backend server
uv run python server.py
```

The backend server will start on `http://localhost:8000`

### 3. MCP Server Setup

In a new terminal:

```bash
# Navigate to MCP server directory
cd mcp_server

# Create virtual environment with uv
uv venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies using pyproject.toml
uv pip install -e .

# Test the MCP server
uv run python server.py
```

### 4. Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "brainrot": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/brainrot-mcp/mcp_server/server.py"],
      "env": {
        "BACKEND_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/brainrot-mcp` with your actual project path.

### 5. Restart Claude Desktop

Restart Claude Desktop to load the new MCP server configuration.

## 🔧 Alternative Setup Methods

### Using pip instead of uv

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python server.py
```

#### MCP Server Setup
```bash
cd mcp_server
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install fastmcp httpx python-dotenv
python server.py
```

### Using conda

```bash
# Backend
cd backend
conda create -n brainrot-backend python=3.12
conda activate brainrot-backend
pip install -r requirements.txt
python server.py

# MCP Server
cd mcp_server
conda create -n brainrot-mcp python=3.12
conda activate brainrot-mcp
pip install fastmcp httpx python-dotenv
python server.py
```

## 🧪 Testing Your Setup

### 1. Test Backend Server

```bash
# Test API endpoint
curl http://localhost:8000/api/contexts

# Should return an empty array: []
```

### 2. Test MCP Server with Inspector

```bash
cd mcp_server
npx @modelcontextprotocol/inspector uv run python server.py
```

This opens a web interface to test MCP tools.

### 3. Test in Claude Desktop

Open Claude Desktop and try these commands:

```
/mcp list_contexts
```

Should show available MCP tools including:
- `push_context` - Store context
- `pop_context` - Retrieve context  
- `list_contexts` - List all contexts
- `delete_context` - Delete context

## 📂 Project Structure

```
brainrot-mcp/
├── backend/              # FastAPI backend server
│   ├── server.py        # Main API server
│   ├── database.py      # SQLite database management
│   ├── models.py        # Pydantic data models
│   ├── requirements.txt # Backend dependencies
│   └── data/            # SQLite database storage
│       └── brainrot.db  # Context storage database
├── mcp_server/          # MCP server implementation
│   ├── server.py        # FastMCP server with context tools
│   ├── pyproject.toml   # Python project configuration
│   ├── requirements.txt # MCP server dependencies
│   └── src/             # Package source code
└── SETUP.md            # This file
```

## 🔧 Environment Configuration

### Backend Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./data/brainrot.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS (if needed for frontend)
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### MCP Server Environment Variables

Create `.env` file in `mcp_server/` directory:

```env
# Backend API URL
BACKEND_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

## 🔍 Troubleshooting

### Common Issues

#### "Failed to reconnect to brainrot"

1. **Check backend server is running:**
   ```bash
   curl http://localhost:8000/api/contexts
   ```

2. **Verify MCP server process:**
   ```bash
   ps aux | grep brainrot
   ```

3. **Check Claude Desktop logs:**
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

#### "Module not found" errors

1. **Ensure virtual environment is activated:**
   ```bash
   which python  # Should point to .venv/bin/python
   ```

2. **Reinstall dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

#### "Port already in use"

1. **Find process using port 8000:**
   ```bash
   lsof -i :8000
   ```

2. **Kill the process:**
   ```bash
   kill -9 <PID>
   ```

#### "Permission denied" when accessing database

1. **Check database directory permissions:**
   ```bash
   ls -la backend/data/
   ```

2. **Create data directory if missing:**
   ```bash
   mkdir -p backend/data
   ```

### Verification Commands

```bash
# Check if backend is responding
curl -s http://localhost:8000/api/contexts | jq '.'

# Test MCP server standalone
cd mcp_server && uv run python -c "import server; print('MCP server imports successfully')"

# Check virtual environment
uv pip list | grep fastmcp

# Verify Python version
python --version  # Should be 3.12+
```

### Log Files

- **Backend logs:** Console output from `python server.py`
- **MCP server logs:** Console output from MCP server
- **Claude Desktop logs:** Check application logs directory

## 🔄 Development Workflow

### Starting Development Session

```bash
# Terminal 1: Backend
cd backend && uv run python server.py

# Terminal 2: MCP Server (for testing)
cd mcp_server && npx @modelcontextprotocol/inspector uv run python server.py

# Terminal 3: Development work
cd brainrot-mcp
```

### Making Changes

1. **Backend changes:** Restart backend server
2. **MCP server changes:** Restart Claude Desktop to reload MCP server
3. **Configuration changes:** Always restart Claude Desktop

## 📱 Usage Examples

Once set up, you can use these commands in Claude Desktop:

```bash
# Store context
push_context("auth-pattern", "Use JWT with refresh tokens", ["architecture", "security"])

# Retrieve context
pop_context("auth-pattern")

# List all contexts
list_contexts()

# List by tag
list_contexts(tag="architecture")

# Delete context
delete_context("auth-pattern")
```

## 🚀 Production Deployment

For production deployment:

1. **Use environment variables for configuration**
2. **Set up proper logging**
3. **Use a process manager (systemd, supervisor)**
4. **Consider using PostgreSQL instead of SQLite**
5. **Set up HTTPS/TLS**
6. **Configure firewalls and security**

## 📞 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review the logs
3. Verify all dependencies are installed
4. Ensure virtual environments are properly activated
5. Check that all services are running on correct ports

---

**Note:** This setup creates a local development environment. For team collaboration or production use, consider deploying the backend server to a shared environment and updating the `BACKEND_URL` in your MCP configuration.