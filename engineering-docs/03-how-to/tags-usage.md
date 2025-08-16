# How Tags Work in Brainrot MCP

## Overview
Tags provide a powerful way to categorize and filter your stored contexts. They enable quick retrieval of related information across your project.

## Storing Context with Tags

When using `push_context`, pass tags as an array of strings:

```python
push_context(
    key="auth-flow",
    content="JWT implementation with refresh tokens...",
    tags=["architecture", "security", "authentication"],
    priority="high"
)
```

## Tag Format
- **Input Format**: Pass tags as an array: `["tag1", "tag2", "tag3"]`
- **Storage**: Tags are stored as JSON arrays in the database
- **Case Sensitive**: Tags are case-sensitive ("TODO" ≠ "todo")

## Filtering by Tags

Use `list_contexts` with a tag parameter to filter:

```python
# Get all security-related contexts
list_contexts(tag="security")

# Get all TODOs
list_contexts(tag="todo")

# Get architecture decisions
list_contexts(tag="architecture")
```

## Best Practices

### Recommended Tag Categories
- **`architecture`** - Design decisions and patterns
- **`todo`** - Tasks to complete
- **`tech-debt`** - Technical debt items
- **`security`** - Security-related decisions
- **`performance`** - Performance optimizations
- **`bug`** - Known issues
- **`feature`** - Feature-specific context
- **`pattern`** - Code patterns and conventions

### Tag Naming Conventions
1. Use lowercase for consistency: `todo` not `TODO`
2. Use hyphens for multi-word tags: `tech-debt` not `tech debt`
3. Be specific but concise: `auth-jwt` not `authentication-using-json-web-tokens`
4. Use consistent naming across your project

## Examples

### Organizing TODOs by Area
```python
push_context("refactor-auth", "Refactor authentication to use middleware", 
            tags=["todo", "backend", "auth"], priority="medium")

push_context("add-rate-limiting", "Add rate limiting to API endpoints",
            tags=["todo", "security", "api"], priority="high")

# Later, get all backend TODOs
list_contexts(tag="backend")
```

### Tracking Technical Debt
```python
push_context("db-n+1-queries", "Multiple N+1 queries in user dashboard",
            tags=["tech-debt", "performance", "database"], priority="high")

# Get all performance-related tech debt
list_contexts(tag="performance")
```

### Architecture Decisions
```python
push_context("event-sourcing", "Use event sourcing for audit trail",
            tags=["architecture", "pattern", "audit"], priority="high")

# Review all architecture decisions
list_contexts(tag="architecture")
```

## Technical Implementation

### How Tags Are Processed
1. MCP framework passes tags as a JSON-encoded string
2. Server parses the JSON string into a Python list
3. Tags are validated and cleaned (trimmed of whitespace)
4. Stored as a JSON array in SQLite database
5. Filtering uses exact string matching

### Database Storage
Tags are stored in a JSON column in SQLite:
```sql
tags JSON DEFAULT '[]'
```

### Tag Filtering Logic
The backend filters contexts by checking if the requested tag exists in the tags array:
```python
for ctx in all_contexts:
    if tag in (ctx.tags or []):
        contexts.append(ctx)
```

## Troubleshooting

### Tags Not Filtering Correctly
- Ensure tags are passed as an array: `["tag1", "tag2"]`
- Check for typos - tags are case-sensitive
- Verify the context was stored with the expected tags using `pop_context(key)`

### Empty Tag Results
- Use `list_contexts()` without parameters to see all contexts
- Check if the tag name matches exactly (case-sensitive)
- Ensure contexts have been stored with that tag

## Future Enhancements
- Tag auto-completion
- Tag renaming across all contexts
- Hierarchical tags (e.g., `backend/auth`)
- Tag statistics and usage analytics