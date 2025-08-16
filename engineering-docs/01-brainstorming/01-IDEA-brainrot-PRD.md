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
# Questions

## Key Clarifications Needed


### 2. Scope Ruthlessness
For the 5-hour MVP, should we:
- Skip delete_context() to save time?
- Focus on just ONE content type (e.g., just architecture decisions)?
- Hard-code certain things (like context expiry)?

#### Answer
HOLD

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



# 