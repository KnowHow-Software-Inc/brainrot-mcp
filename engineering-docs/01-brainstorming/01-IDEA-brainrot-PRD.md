# MCP Context Manager - Product Requirements Document

## Initial Discovery

### Problem Statement
Developers using AI coding agents lose valuable project context between sessions, leading to repetitive explanations and inconsistent code patterns. Current solutions require switching between tools, breaking the coding flow.

### Core Value Proposition
An MCP server that seamlessly captures, stores, and retrieves project context within AI coding sessions, enabling persistent knowledge and architecture consistency.

### MVP User Flows

#### Flow 1: Context Persistence
1. Developer works on feature, encounters complex business logic
2. Saves context: `store_context("user-auth", "Users can have multiple roles, admin overrides...", type="decision")`
3. Next session: `get_context("user-auth")` returns saved context
4. AI agent has full context without re-explanation

#### Flow 2: Architecture Validation
1. Developer saves code snippet: `store_context("repo-pattern", code_snippet, type="code")`
2. Later: `validate_against_context(new_code, "repo-pattern")` 
3. AI compares new code to stored patterns and returns compliance feedback

### MVP Features (Phase 1 - CRUD)
- `store_context(key, content, type)` - Save project knowledge (code/decisions/requirements)
- `get_context(key)` - Retrieve stored context  
- `list_contexts()` - Show all stored items
- `delete_context(key)` - Remove stored context

### MVP Features (Phase 2 - AI Validation)
- `validate_against_context(content, reference_key)` - AI-powered comparison
- `get_all_relevant_context(query)` - AI-powered context search

### Success Criteria
- Store & retrieve context in under 2 seconds
- Support code snippets, decisions, requirements
- AI validation provides actionable feedback
- Works seamlessly in Claude Code session

### Development Approach
- Phase 1: Focus on CRUD operations and basic I/O
- Phase 2: Add AI-powered validation using Anthropic API keys
- Target: 5-hour hackathon timeline with core value loop delivery