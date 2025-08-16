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


# Questions

## Key Clarifications Needed

### 1. Demo Scenario
What's the ONE killer demo you want to show judges? Like "Watch me save architecture decisions in session 1, then in session 2 the AI automatically knows them" - what's YOUR version?

### 2. Scope Ruthlessness
For the 5-hour MVP, should we:
- Skip delete_context() to save time?
- Focus on just ONE content type (e.g., just architecture decisions)?
- Hard-code certain things (like context expiry)?

### 3. Context Organization
- Flat key-value store OR hierarchical (project > module > context)?
- Single namespace per user OR project-based isolation?
- Overwrite on duplicate keys OR version history?

### 4. Success Metric
What's the ONE thing that MUST work for you to feel successful?
- "I can store and retrieve context" OR
- "I can validate code against stored patterns" OR
- Something else?

### 5. Non-goals
What should we explicitly NOT do? (e.g., no UI, no auth, no multi-user collaboration)

### 6. Integration Point
How do you envision using this in Claude Code? Through explicit commands or should it auto-capture certain things?


# Killer Demo
## Demo Idea 1 - push and pop
1. Send context to brainrot
2. Retrieve context on another IDE and continue working

## Demo Idea 2 - preset context
1. Store context about a project goal (example: build frontend, todos)
2. Retrieve it later in order to:
	1. Build long running plans
	2. Manage tech debt
	3. Onboard new developers

## Demo Idea 3 - claude code to claude desktop
1. Send context about architecture or ideas to brainrot
2. Retrieve context for assessment, review, validation, challenge in another model (gpt 5, gemini, etc etc)
3. Send report back to brainrot
4. Retrieve report in original claude code session

## Demo Idea 4 - async validation and research
1. Send context about architecture, issues, code, plans etc to brainrot
2. AI works on it async
3. Brainrot documents results
4. Retrieve results later


## Implied technical requirements
1. Semantic tagging
2. I/O 