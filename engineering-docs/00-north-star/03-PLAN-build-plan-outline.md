# Revised 6-Phase Plan (Demo-Aligned)

## Phase 1: Minimal Backend - Demo 1 Foundation
**Implement in:** backend/models.py, backend/server.py

**Tasks:**
- Add SQLAlchemy Context model (inherits database.Base) with columns: id, project, key (unique with project), content, created_at, updated_at (use UTC)
- Add Pydantic schemas: ContextCreate (key, content, optional project), ContextOut
- Import models before table creation in backend/server.py (add `import models # noqa: F401` at top)
- Keep existing import style: `from database import DatabaseManager` (no changes needed)
- Add endpoints:
  - POST /api/contexts: create-or-replace; default project="default" if missing; return 201 if new, 200 if overwriting
  - GET /api/contexts/{key}?project=...: fetch by key within project (default "default"); return 200 if found, 404 if missing
- Keep current DB path ./data/brainrot.db to ship fast; env override already supported

**Exit:** curl -X POST ... then curl GET ... works; unknown key returns 404

## Phase 2: Minimal MCP - Demo 1 Tools (Stubbed)
**Implement in:** mcp_server/main.py

**Tasks:**
- Define two tools with simple schemas: store_context(key, content) and get_context(key)
- Return stubbed success/data for inspector validation

**Exit:** Tools visible and invokable in inspector

## Phase 3: Connect & Verify - Demo 1 Complete
**Implement in:** mcp_server/main.py

**Tasks:**
- Compute project = os.path.basename(os.getcwd()) in the MCP server (allow BRAINROT_PROJECT env override)
- Wire tools to backend via requests: POST/GET; map HTTP 404 to a clear tool error
- Backend accepts optional project in body (POST) or query param (GET); defaults to "default" if omitted
- MCP always sends project parameter explicitly

**Exit:** Store in one session, retrieve in another for same project

## Phase 4: Extended Backend - Demo 2 Foundation
**Implement in:** backend/models.py, backend/server.py

**Tasks:**
- Add tags as JSON-encoded TEXT column (default "[]")
- Extend POST to accept tags
- Add GET /api/contexts with optional ?tag=foo using simple LIKE '%"foo"%' filter (note: substring-prone but acceptable for demo); order by updated_at DESC
- Always set created_at on insert, always bump updated_at on create/replace (use UTC)

**Exit:** Store with tags=["todo"], list all, list by tag

## Phase 5: Extended MCP - Demo 2 Tools
**Implement in:** mcp_server/main.py

**Tasks:**
- Add list_contexts(filter_by_tag) returning minimal fields
- Keep store_context as create-or-replace; skip separate update_context and delete_context to stay lean and align with PRD Non-Goals

**Exit:** Tag-filtered list works in inspector

## Phase 6: Polish & Desktop - Demo 2 Complete
**Implement in:** README.md (root), simple demo script snippets

**Tasks:**
- Document: run backend from backend/ directory (`cd backend && uvicorn server:app --reload`), run MCP server, Claude Desktop config
- Include copy-paste demo commands for Demos 1 and 2

**Exit:** Both demos reproducible quickly

## Parallel Work Opportunities

### Phase 1 & 2 can run in parallel
- **Phase 1** (Backend): Creating SQLAlchemy models and API endpoints
- **Phase 2** (MCP): Setting up FastMCP server with tool definitions
- These are completely independent until Phase 3 connects them

### Phase 4 & 5 can run in parallel  
- **Phase 4** (Backend): Adding tags and list/filter endpoints
- **Phase 5** (MCP): Adding list_contexts tool (no update_context needed with create-or-replace)
- Same pattern - independent until integration

## Implementation Notes

### Key Alignment Points
- **DB path:** Keeping ./data/brainrot.db reduces friction; DATABASE_URL allows switching to ~/.brainrot/brainrot.db later with no code change
- **SQLAlchemy 2.0:** Use `from sqlalchemy.orm import declarative_base` (not sqlalchemy.ext.declarative) to avoid deprecation
- **Uniqueness:** Add unique constraint on (project, key) in the Context model
- **Defaults:** Backend should default project="default" when missing to keep Phase 1 simple; Phase 3 MCP sends real project
- **Status codes:** 201 on create, 200 on overwrite/get, 404 on missing
- **Timestamps:** Always use UTC; set created_at on insert, always bump updated_at on create/replace
- **Run location:** Backend runs from backend/ directory with `cd backend && uvicorn server:app --reload`
- **Import style:** Keep existing imports (`from database import DatabaseManager`) - no package changes needed
- **Out of scope to stay lean:** delete tool/endpoint, migrations, pagination, complex tag queries

## Why This Split Works:

**Phases 1-3:** Laser-focused on Demo 1 (basic store/retrieve)
- Each phase ~1 hour
- Phase 3 proves the architecture works

**Phases 4-6:** Builds Demo 2 (project management with tags)
- Adds complexity incrementally
- Phase 6 makes it production-ready

**Key benefits:**
- **Testable progress:** Each phase has one clear deliverable
- **Demo-driven:** Phase 3 = Demo 1 works, Phase 6 = Demo 2 works
- **Risk reduction:** We validate the MCP↔Backend connection early (Phase 3)
- **Fail-fast:** If MCP integration is problematic, we know by Phase 3