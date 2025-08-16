# MCP Context Manager - Product Requirements Document

## Initial Discovery

### Problem Statement
Developers using AI coding agents lose valuable project context between sessions, leading to repetitive explanations and inconsistent code patterns. Current solutions require switching between tools, breaking the coding flow.

### Core Value Proposition
An MCP server that seamlessly captures, stores, and retrieves project context within AI coding sessions, enabling persistent knowledge and architecture consistency.

## Goal: Our Killer Demos

### The Killer Combo Demo
"Watch me save architecture decisions and TODOs in Claude Code, switch to VS Code to continue work with full context, then validate my changes against the original architecture - all without losing any project knowledge."

This hits Demos 1, 2, and sets up for 3. Achievable in 5 hours.

### Demo 1: Cross-IDE Context Sharing (Phase 1)
**Scenario:** Developer saves context in Claude Code, retrieves in VS Code
1. Store architecture decision: `store_context("auth-pattern", "Use JWT with refresh tokens", tags=["architecture"])`
2. Switch to VS Code with different AI assistant
3. Retrieve context: `get_context("auth-pattern")` 
4. Continue development with full context preserved

### Demo 2: Long-Running Project Management (Phase 1)
**Scenario:** Managing TODOs and technical debt across sessions
1. Store project goals: `store_context("sprint-goals", "Complete user auth flow", tags=["goals"])`
2. Track tech debt: `store_context("tech-debt-auth", "Refactor token validation", tags=["tech-debt"])`
3. New session days later: `list_contexts(filter_by_tag="tech-debt")`
4. Retrieve and address accumulated items systematically

### Demo 3: Cross-Model Collaboration (Phase 2)
**Scenario:** Architecture validation across different AI models
1. Store pattern in Claude: `store_context("repo-pattern", code_snippet, tags=["pattern"])`
2. Export for review: `export_context("repo-pattern", format="standard")`
3. Import in GPT/Gemini session for alternative perspective
4. Store feedback: `store_context("repo-pattern-review", feedback)`
5. Retrieve combined insights in original Claude session 

### Demo Implied Requirements Analysis

**Demo 1 (Push/Pop)** - Simplest foundation
- Basic store/retrieve
- Cross-IDE context sharing
- Core CRUD only

**Demo 2 (Preset Context)** - Builds on Demo 1
- Same CRUD + categorization (goals, todos, tech debt)
- Enables long-running project management
- Still just storage/retrieval

**Demo 3 (Cross-Model)** - Adds interoperability
- CRUD + cross-platform context format
- Enables multi-AI collaboration
- Requires standardized context structure

**Demo 4 (Async)** - Most complex
- Everything above + async processing
- Background AI analysis
- Result storage

### Recommended Feature Prioritization

**Phase 1 Core (Hour 1-2)** - Enables Demos 1 & 2
- `store_context(key, content, metadata)` with tags/categories
- `get_context(key)` 
- `list_contexts(filter_by_tag)`
- Flat key-value with metadata tags

**Phase 2 Enhancement (Hour 3)** - Enables Demo 3
- Standardized context format (JSON with type, content, metadata)
- `export_context(key, format)` for cross-platform
- `import_context(data)`

**Phase 3 Stretch (Hour 4-5)** - Partially enables Demo 4
- `queue_for_analysis(key)` 
- `get_analysis_results(key)`
- Simple async flag, not full background processing
### Success Criteria
- Store & retrieve context in under 2 seconds
- Support code snippets, decisions, requirements
- AI validation provides actionable feedback
- Works seamlessly in Claude Code session

## Technical Specifications & Approach

### Core Architecture Decisions

**Storage System**
- SQLite database for persistence
- Location: `~/.brainrot/brainrot.db`
- Schema optimized for fast key-value retrieval with metadata filtering

**Context Organization**
- Flat key-value store (no hierarchical nesting)
- Project-based isolation using current working directory as project ID
- Keys are simple strings: `auth-pattern`, `sprint-goals`, etc.
- Overwrite on duplicate keys (no version history for MVP)

**Project Detection**
- Use current working directory name as project identifier
- Example: `/Users/dev/myapp/` → project = "myapp"
- Contexts are scoped to projects automatically

**Data Model**
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

### MCP Integration
- Expose tools via MCP server
- Explicit command invocation only (no auto-capture)
- Tools available in any MCP-compatible client (Claude Code, VS Code, etc.)

### Phase 1 Core Tools (Hour 1-2)
- `store_context(key, content, tags)` - Save with optional tags
- `get_context(key)` - Retrieve by exact key
- `list_contexts(filter_by_tag)` - List all or filter by tag
- All operations scoped to current project

### Phase 2 Tools (Hour 3)
- `export_context(key, format)` - Export for cross-platform use
- `import_context(data)` - Import from other systems
- Standardized JSON format for interoperability

### Non-Goals (Explicit Exclusions)
- No authentication or user management
- No multi-user collaboration
- No UI (stretch goal only if ahead of schedule)
- No delete functionality (save time)
- No version history
- No context expiry
- No auto-capture or intelligent detection
