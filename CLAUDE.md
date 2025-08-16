# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KnowHow MCP is a Model Context Protocol server that bridges AI coding sessions with human expertise. It allows developers to seamlessly request help from other developers without leaving their AI-assisted coding flow.

## Architecture

The system consists of three main components:

1. **MCP Server** (`mcp_server/`) - Exposes tools for creating help requests and checking responses
2. **Backend API** (`backend/`) - FastAPI server managing SQLite database and REST endpoints
3. **Web Dashboard** (`frontend/`) - Single HTML page for viewing and responding to help requests

Communication flow:
- MCP Server → HTTP requests → Backend API → SQLite database
- Web Dashboard → Fetch API → Backend API

## Development Commands

Since this is a hackathon project in active development, key commands will be:

```bash
# Backend API
cd backend
pip install -r requirements.txt
python server.py  # Runs on port 8000

# MCP Server
cd mcp_server
pip install -r requirements.txt
python server.py  # For MCP Inspector testing

# Test MCP Server
npx @modelcontextprotocol/inspector python mcp_server/server.py

# Frontend
# Simply open frontend/index.html in browser or serve it
python -m http.server 8080 --directory frontend
```

## MCP Tools

The server exposes four main tools:
- `post_help_request` - Creates help request with sanitized context
- `check_responses` - Retrieves responses for user's requests
- `list_my_requests` - Shows all requests by current user
- `provide_help` - Allows responding to others' requests

## Key Implementation Details

- **Database**: SQLite file at `data/knowhow.db` (auto-created on first run)
- **API Base URL**: Backend runs on `http://localhost:8000`
- **Security**: Context sanitization removes secrets/tokens before posting
- **Demo Mode**: Pre-seeded data for hackathon demonstration

## Current Development Phase

Following the 8-hour hackathon timeline in `planning-notes/01-brainstorming/PRD-and-Plan.md`. Priority is on achieving a complete value loop demonstration rather than polish.