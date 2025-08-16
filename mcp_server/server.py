#!/usr/bin/env python3
"""
Brainrot MCP Server - Context Management for AI Coding Sessions
"""

import os
import json
import httpx
import subprocess
import time
import atexit
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Backend process tracking
_backend_process = None

# Initialize MCP server
mcp = FastMCP("brainrot-context-manager")


def start_backend():
    """Start the backend API server if it's not already running."""
    global _backend_process
    
    # Check if backend is already running
    try:
        with httpx.Client() as client:
            response = client.get(f"{BACKEND_URL}/", timeout=2.0)
            if response.status_code == 200:
                print(f"✅ Backend already running at {BACKEND_URL}")
                return
    except:
        pass  # Backend not running, we'll start it
    
    # Start the backend
    backend_dir = Path(__file__).parent.parent / "backend"
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        return
    
    print(f"🚀 Starting backend server at {BACKEND_URL}...")
    try:
        _backend_process = subprocess.Popen(
            ["uv", "run", "python", "server.py"],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Verify it started
        try:
            import httpx
            with httpx.Client() as client:
                response = client.get(f"{BACKEND_URL}/", timeout=5.0)
                if response.status_code == 200:
                    print(f"✅ Backend started successfully at {BACKEND_URL}")
                else:
                    print(f"⚠️ Backend may not have started properly")
        except:
            print(f"⚠️ Backend startup verification failed")
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")


def cleanup_backend():
    """Clean up the backend process on exit."""
    global _backend_process
    if _backend_process:
        print("🛑 Stopping backend server...")
        _backend_process.terminate()
        _backend_process.wait(timeout=5)


# Register cleanup function
atexit.register(cleanup_backend)


def summarize_content(content: str, max_length: int = 500) -> str:
    """
    Create a summary of the content for storage.
    This is a simple truncation for now, but could be enhanced with AI summarization.
    """
    if len(content) <= max_length:
        return content
    
    # Find a good break point (end of sentence or paragraph)
    truncated = content[:max_length]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    
    break_point = max(last_period, last_newline)
    if break_point > max_length * 0.7:  # If we found a good break point
        return truncated[:break_point + 1] + "..."
    else:
        return truncated + "..."


@mcp.tool()
async def push_context(
    key: str,
    content: str,
    tags: Optional[Union[List[str], str]] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Push (store) context from the current session for later retrieval.
    
    This tool captures important context like architecture decisions, code patterns,
    TODOs, or any other information you want to persist between sessions.
    
    Args:
        key: Unique identifier for this context (e.g., "auth-pattern", "todo-refactor-api")
        content: The full context to store
        tags: Tags for categorization - can be array ["architecture", "security"] or string "architecture,security"
        priority: Priority level (low, medium, high) - useful for TODOs and tech debt
    
    Returns:
        Confirmation of storage with the key and summary
    
    Examples:
        - push_context("auth-flow", "JWT with refresh tokens...", ["security", "architecture"])
        - push_context("todo-validation", "Add input validation to user endpoints", ["todo", "backend"])
    """
    try:
        # Create a summary of the content
        summary = summarize_content(content, max_length=200)
        
        # Parse tags - handle both array and string inputs
        parsed_tags = []
        if tags:
            if isinstance(tags, list):
                # If it's already a list, use it directly
                parsed_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
            elif isinstance(tags, str) and tags.strip():
                # If it's a string, split by comma
                parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Prepare the context data
        context_data = {
            "key": key,
            "content": content,
            "summary": summary,
            "tags": parsed_tags,
            "context_metadata": {
                "priority": priority,
                "source": "mcp_push",
                "char_count": len(content)
            }
        }
        
        # Send to backend
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/contexts",
                json=context_data,
                timeout=10.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "key": result["key"],
                "summary": result["summary"],
                "tags": result["tags"],
                "message": f"Context '{key}' stored successfully",
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at")
            }
            
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Failed to store context: {str(e)}",
            "key": key
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "key": key
        }


@mcp.tool()
async def pop_context(
    key: str,
    include_instructions: bool = True
) -> Dict[str, Any]:
    """
    Pop (retrieve) previously stored context by its key.
    
    This tool retrieves context that was stored in a previous session,
    allowing you to restore important information like architecture decisions,
    code patterns, or TODOs.
    
    Args:
        key: The unique identifier of the context to retrieve
        include_instructions: Whether to include instructions on how to apply the context
    
    Returns:
        The stored context with optional instructions for application
    
    Examples:
        - pop_context("auth-flow")  # Retrieve authentication pattern
        - pop_context("todo-validation")  # Get TODO item details
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/contexts/{key}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"No context found with key '{key}'",
                    "suggestion": "Use list_contexts() to see available context keys"
                }
            
            response.raise_for_status()
            result = response.json()
            
            # Prepare the response
            context_response = {
                "success": True,
                "key": result["key"],
                "content": result["content"],
                "summary": result.get("summary"),
                "tags": result.get("tags", []),
                "priority": result.get("context_metadata", {}).get("priority") if result.get("context_metadata") else None,
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at")
            }
            
            # Add instructions if requested
            if include_instructions:
                instructions = generate_context_instructions(result)
                context_response["instructions"] = instructions
            
            return context_response
            
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Failed to retrieve context: {str(e)}",
            "key": key
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "key": key
        }


@mcp.tool()
async def list_contexts(
    tag: str = "",
    limit: int = 20
) -> Dict[str, Any]:
    """
    List all available contexts, optionally filtered by tag.
    
    This helps you discover what contexts are available from previous sessions.
    
    Args:
        tag: Optional tag to filter by (e.g., "todo", "architecture", "tech-debt")
        limit: Maximum number of contexts to return (default: 20)
    
    Returns:
        List of available contexts with their keys, summaries, and tags
    
    Examples:
        - list_contexts()  # Show all contexts
        - list_contexts(tag="todo")  # Show only TODO items
        - list_contexts(tag="architecture")  # Show architecture decisions
    """
    try:
        async with httpx.AsyncClient() as client:
            params = {}
            if tag and tag.strip():
                params["tag"] = tag.strip()
                
            response = await client.get(
                f"{BACKEND_URL}/api/contexts",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            
            contexts = response.json()
            
            # Limit the results
            contexts = contexts[:limit]
            
            # Format for display
            formatted_contexts = []
            for ctx in contexts:
                formatted_contexts.append({
                    "key": ctx["key"],
                    "summary": ctx.get("summary", ctx["content"][:100] + "..."),
                    "tags": ctx.get("tags", []),
                    "priority": ctx.get("context_metadata", {}).get("priority") if ctx.get("context_metadata") else None,
                    "updated_at": ctx.get("updated_at")
                })
            
            return {
                "success": True,
                "count": len(formatted_contexts),
                "contexts": formatted_contexts,
                "filter": {"tag": tag} if tag and tag.strip() else None
            }
            
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Failed to list contexts: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@mcp.tool()
async def search_contexts(
    query: str,
    limit: int = 10,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Search contexts using semantic similarity.
    
    This tool uses vector embeddings to find contexts that are semantically similar
    to your query, even if they don't contain the exact keywords.
    
    Args:
        query: What you're looking for (e.g., "authentication patterns", "database setup")
        limit: Maximum number of results to return (default: 10)
        threshold: Minimum similarity score (0.0-1.0, default: 0.5)
    
    Returns:
        List of contexts ranked by semantic similarity with similarity scores
    
    Examples:
        - search_contexts("JWT authentication")  # Find auth-related contexts
        - search_contexts("error handling patterns", limit=5)  # Find error handling approaches
        - search_contexts("database configuration", threshold=0.7)  # High-confidence matches only
    """
    try:
        if not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty"
            }
        
        async with httpx.AsyncClient() as client:
            params = {
                "query": query.strip(),
                "limit": limit,
                "threshold": threshold
            }
            
            response = await client.get(
                f"{BACKEND_URL}/api/contexts/search/semantic",
                params=params,
                timeout=15.0
            )
            response.raise_for_status()
            
            contexts = response.json()
            
            # Format for display
            formatted_contexts = []
            for ctx in contexts:
                similarity_score = ctx.get("context_metadata", {}).get("similarity_score", 0)
                formatted_contexts.append({
                    "key": ctx["key"],
                    "content": ctx["content"],
                    "summary": ctx.get("summary"),
                    "tags": ctx.get("tags", []),
                    "priority": ctx.get("context_metadata", {}).get("priority") if ctx.get("context_metadata") else None,
                    "similarity_score": round(similarity_score, 3),
                    "updated_at": ctx.get("updated_at")
                })
            
            return {
                "success": True,
                "query": query,
                "count": len(formatted_contexts),
                "contexts": formatted_contexts,
                "search_params": {
                    "limit": limit,
                    "threshold": threshold
                }
            }
            
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Failed to search contexts: {str(e)}",
            "query": query
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "query": query
        }


@mcp.tool()
async def delete_context(key: str) -> Dict[str, Any]:
    """
    Delete a context by its key.
    
    Use this to remove contexts that are no longer relevant.
    
    Args:
        key: The unique identifier of the context to delete
    
    Returns:
        Confirmation of deletion
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{BACKEND_URL}/api/contexts/{key}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"No context found with key '{key}'"
                }
            
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Context '{key}' deleted successfully"
            }
            
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"Failed to delete context: {str(e)}",
            "key": key
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "key": key
        }


def generate_context_instructions(context: Dict[str, Any]) -> str:
    """
    Generate instructions based on the context type and tags.
    """
    tags = context.get("tags", [])
    content = context.get("content", "")
    
    instructions = []
    
    # Architecture decisions
    if "architecture" in tags:
        instructions.append("📐 ARCHITECTURE DECISION:")
        instructions.append("Apply this architectural pattern consistently across the codebase.")
        instructions.append("Consider its implications for related components.")
    
    # TODOs
    elif "todo" in tags:
        instructions.append("✅ TODO ITEM:")
        instructions.append("This task needs to be completed.")
        priority = context.get("context_metadata", {}).get("priority") if context.get("context_metadata") else "medium"
        if priority == "high":
            instructions.append("⚠️ HIGH PRIORITY - Address this immediately.")
        elif priority == "low":
            instructions.append("📝 LOW PRIORITY - Can be addressed later.")
    
    # Technical debt
    elif "tech-debt" in tags or "tech_debt" in tags:
        instructions.append("🔧 TECHNICAL DEBT:")
        instructions.append("This represents accumulated technical debt that should be addressed.")
        instructions.append("Consider refactoring when touching related code.")
    
    # Security
    elif "security" in tags:
        instructions.append("🔒 SECURITY CONSIDERATION:")
        instructions.append("Ensure this security pattern is properly implemented.")
        instructions.append("Review for potential vulnerabilities.")
    
    # Code patterns
    elif "pattern" in tags:
        instructions.append("🎯 CODE PATTERN:")
        instructions.append("Use this pattern for similar implementations.")
        instructions.append("Maintain consistency with this approach.")
    
    # Default
    else:
        instructions.append("📌 STORED CONTEXT:")
        instructions.append("Apply this information as appropriate to your current task.")
    
    return "\n".join(instructions)


# Resources for providing context information
@mcp.resource("context://summary")
async def get_context_summary() -> str:
    """
    Get a summary of all stored contexts.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/contexts",
                timeout=10.0
            )
            response.raise_for_status()
            
            contexts = response.json()
            
            # Group by tags
            by_tag = {}
            for ctx in contexts:
                for tag in ctx.get("tags", ["untagged"]):
                    if tag not in by_tag:
                        by_tag[tag] = []
                    by_tag[tag].append(ctx["key"])
            
            # Format summary
            lines = ["# Stored Contexts Summary\n"]
            lines.append(f"Total contexts: {len(contexts)}\n")
            
            for tag, keys in sorted(by_tag.items()):
                lines.append(f"\n## {tag.upper()} ({len(keys)} items)")
                for key in keys[:5]:  # Show first 5
                    lines.append(f"  - {key}")
                if len(keys) > 5:
                    lines.append(f"  ... and {len(keys) - 5} more")
            
            return "\n".join(lines)
            
    except Exception as e:
        return f"Error getting context summary: {str(e)}"


# Prompts for context management workflows
@mcp.prompt()
async def analyze_project_context() -> str:
    """
    Analyze and summarize the current project's stored context.
    
    This prompt helps review all stored contexts to understand the project's
    architecture decisions, technical debt, and outstanding TODOs.
    """
    try:
        # Get all contexts
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/contexts",
                timeout=10.0
            )
            response.raise_for_status()
            contexts = response.json()
        
        if not contexts:
            return "No contexts found. Use push_context() to store project information."
        
        # Group by tags
        by_tag = {}
        for ctx in contexts:
            tags = ctx.get("tags", ["untagged"])
            for tag in tags:
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(ctx)
        
        # Generate analysis
        analysis = ["# Project Context Analysis\n"]
        analysis.append(f"**Total Contexts:** {len(contexts)}\n")
        
        # High priority items first
        high_priority = [ctx for ctx in contexts if ctx.get("context_metadata", {}).get("priority") == "high"]
        if high_priority:
            analysis.append("## 🚨 High Priority Items")
            for ctx in high_priority:
                summary = ctx.get("summary", ctx["content"][:100] + "...")
                analysis.append(f"- **{ctx['key']}**: {summary}")
                analysis.append(f"  Tags: {', '.join(ctx.get('tags', []))}")
            analysis.append("")
        
        # By category
        for tag, items in sorted(by_tag.items()):
            if tag == "untagged":
                continue
            analysis.append(f"## {tag.upper()} ({len(items)} items)")
            for ctx in items[:3]:  # Show first 3
                summary = ctx.get("summary", ctx["content"][:100] + "...")
                analysis.append(f"- **{ctx['key']}**: {summary}")
            if len(items) > 3:
                analysis.append(f"  ... and {len(items) - 3} more")
            analysis.append("")
        
        return "\n".join(analysis)
        
    except httpx.HTTPError as e:
        return f"Error retrieving contexts from backend: {str(e)}"
    except Exception as e:
        return f"Error analyzing project context: {str(e)}"


@mcp.prompt()
async def suggest_next_actions() -> str:
    """
    Suggest next actions based on stored TODOs and technical debt.
    
    This prompt reviews stored contexts to prioritize what should be worked on next.
    """
    try:
        # Get all contexts and filter for TODOs and tech debt
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/contexts",
                timeout=10.0
            )
            response.raise_for_status()
            contexts = response.json()
        
        # Filter for TODOs and tech debt
        todos = [ctx for ctx in contexts if "todo" in ctx.get("tags", [])]
        debts = [ctx for ctx in contexts if "tech-debt" in ctx.get("tags", []) or "tech_debt" in ctx.get("tags", [])]
        
        suggestions = ["# Suggested Next Actions\n"]
        
        # High priority TODOs
        high_priority_todos = [t for t in todos if t.get("context_metadata", {}).get("priority") == "high"]
        if high_priority_todos:
            suggestions.append("## 🔥 Immediate Actions (High Priority TODOs)")
            for todo in high_priority_todos:
                summary = todo.get("summary", todo["content"][:100] + "...")
                suggestions.append(f"1. **{todo['key']}**: {summary}")
            suggestions.append("")
        
        # Technical debt opportunities
        if debts:
            suggestions.append("## 🔧 Technical Debt to Address")
            for debt in debts[:3]:
                summary = debt.get("summary", debt["content"][:100] + "...")
                suggestions.append(f"- **{debt['key']}**: {summary}")
            suggestions.append("")
        
        # Regular TODOs
        regular_todos = [t for t in todos if t.get("context_metadata", {}).get("priority") != "high"]
        if regular_todos:
            suggestions.append("## 📝 Other TODOs")
            for todo in regular_todos[:5]:
                priority = todo.get("context_metadata", {}).get("priority", "medium")
                summary = todo.get("summary", todo["content"][:100] + "...")
                suggestions.append(f"- **{todo['key']}** ({priority}): {summary}")
            suggestions.append("")
        
        if len(suggestions) == 1:  # Only header
            suggestions.append("No TODOs or technical debt found.")
            suggestions.append("Consider using push_context() to track tasks and improvements.")
        
        return "\n".join(suggestions)
        
    except httpx.HTTPError as e:
        return f"Error retrieving contexts from backend: {str(e)}"
    except Exception as e:
        return f"Error suggesting next actions: {str(e)}"


@mcp.prompt()
async def context_for_feature(feature_name: str) -> str:
    """
    Get relevant context for implementing a specific feature.
    
    This prompt searches stored contexts for patterns, decisions, and considerations
    relevant to implementing a new feature.
    
    Args:
        feature_name: Name or description of the feature to implement
    """
    try:
        # Make HTTP request to backend to get all contexts
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/contexts",
                timeout=10.0
            )
            response.raise_for_status()
            
            contexts = response.json()
            
        if not contexts:
            return "No stored contexts found. Consider storing architectural decisions and patterns first."
        
        # Search for relevant contexts (simple keyword matching)
        feature_keywords = feature_name.lower().split()
        relevant_contexts = []
        
        for ctx in contexts:
            content_lower = (ctx.get("summary", "") + " " + ctx.get("key", "")).lower()
            if any(keyword in content_lower for keyword in feature_keywords):
                relevant_contexts.append(ctx)
        
        response_lines = [f"# Context for Feature: {feature_name}\n"]
        
        if relevant_contexts:
            response_lines.append("## 🎯 Directly Relevant Contexts")
            for ctx in relevant_contexts:
                summary = ctx.get("summary", ctx["content"][:100] + "...")
                response_lines.append(f"- **{ctx['key']}**: {summary}")
                response_lines.append(f"  Tags: {', '.join(ctx.get('tags', []))}")
            response_lines.append("")
        
        # Always show architecture and security contexts
        arch_contexts = [ctx for ctx in contexts if "architecture" in ctx.get("tags", [])]
        if arch_contexts:
            response_lines.append("## 📐 Architecture Decisions to Consider")
            for ctx in arch_contexts[:3]:
                summary = ctx.get("summary", ctx["content"][:100] + "...")
                response_lines.append(f"- **{ctx['key']}**: {summary}")
            response_lines.append("")
        
        security_contexts = [ctx for ctx in contexts if "security" in ctx.get("tags", [])]
        if security_contexts:
            response_lines.append("## 🔒 Security Considerations")
            for ctx in security_contexts[:3]:
                summary = ctx.get("summary", ctx["content"][:100] + "...")
                response_lines.append(f"- **{ctx['key']}**: {summary}")
            response_lines.append("")
        
        if not relevant_contexts and not arch_contexts and not security_contexts:
            response_lines.append("No directly relevant contexts found.")
            response_lines.append("Consider reviewing all stored contexts or adding feature-specific context.")
        
        return "\n".join(response_lines)
        
    except httpx.HTTPError as e:
        return f"Error retrieving contexts from backend: {str(e)}"
    except Exception as e:
        return f"Error getting context for feature: {str(e)}"


@mcp.prompt()
async def assemble_context_guide() -> str:
    """
    Guide for assembling rich context from multiple sources (files, websites, code) and storing it in Brainrot.
    
    This prompt provides step-by-step instructions for gathering comprehensive context
    from various sources and creating well-structured context entries.
    """
    guide_text = """# 📚 Context Assembly Guide

## Overview
Learn how to gather comprehensive context from multiple sources and store it effectively in Brainrot for future AI sessions.

## 🎯 What Makes Good Context?

**Rich, Multi-Source Context Includes:**
- Code snippets with explanations
- Architecture decisions and rationale  
- External documentation and best practices
- Requirements and constraints
- Examples and patterns

## 🔄 Step-by-Step Assembly Process

### 1. Identify Your Context Topic
Choose a clear, specific key for your context:

Examples:
- "user-auth-jwt-pattern"
- "database-migration-strategy" 
- "error-handling-frontend"
- "api-rate-limiting-approach"

### 2. Gather Information from Multiple Sources

#### 📁 From Local Files
Read relevant code files:
- Configuration files (package.json, requirements.txt, etc.)
- Implementation files (.js, .py, .java, etc.)
- Documentation files (README.md, DOCS.md, etc.)
- Test files for usage examples

#### 🌐 From Web Sources
Use WebSearch to find:
- Official documentation
- Best practices articles
- Stack Overflow solutions
- GitHub examples
- Blog posts from experts

#### 🔍 From Existing Codebase
Search your codebase for:
- Similar patterns already implemented
- Related utility functions
- Error handling approaches
- Testing strategies

### 3. Assemble Comprehensive Context

#### Template for Rich Context:
## Overview
[Brief description of what this context covers]

## Implementation Details
[Code snippets, configurations, key files]

## Architecture Rationale
[Why this approach was chosen, trade-offs considered]

## External References
[Links to documentation, articles, examples]

## Usage Examples
[How to apply this pattern, common use cases]

## Gotchas & Considerations
[Known issues, edge cases, things to watch out for]

## Related Patterns
[Links to other contexts or approaches]

## 🛠️ Practical Assembly Examples

### Example 1: JWT Authentication Pattern
1. Read your auth implementation files
2. Research JWT best practices online
3. Assemble comprehensive context including:
   - Current implementation code
   - Security considerations from research
   - Configuration examples
   - Testing approaches
4. Store with tags: ["authentication", "security", "jwt", "architecture"]

### Example 2: Database Schema Design
1. Read migration files and model code
2. Research database best practices
3. Document design decisions and rationale
4. Include performance considerations
5. Store with tags: ["database", "schema", "users", "architecture"]

## 🏷️ Effective Tagging Strategy

### Primary Categories
- `architecture` - High-level design decisions
- `security` - Security patterns and considerations
- `performance` - Optimization strategies
- `testing` - Testing approaches and patterns
- `deployment` - Infrastructure and deployment
- `api` - API design and implementation
- `frontend` - UI/UX patterns and components
- `backend` - Server-side implementation
- `database` - Data modeling and queries

### Secondary Tags
- `todo` - Tasks to be completed
- `tech-debt` - Known issues to address
- `pattern` - Reusable code patterns
- `config` - Configuration management
- `monitoring` - Logging and observability

### Priority Levels
- `high` - Critical decisions, urgent TODOs
- `medium` - Important patterns, regular tasks
- `low` - Nice-to-have improvements, references

## 📋 Assembly Workflow

1. **Start with a Clear Goal**
   - What specific knowledge do you want to preserve?
   - Who will use this context later?

2. **Gather from Multiple Sources**
   - Read 2-3 relevant code files
   - Search web for best practices
   - Check existing contexts for related patterns

3. **Structure the Information**
   - Use markdown headers for organization
   - Include code snippets with explanations
   - Add external links for deeper reading

4. **Store with Rich Metadata**
   - Choose descriptive, searchable key
   - Add 3-5 relevant tags
   - Set appropriate priority level

5. **Cross-Reference Related Contexts**
   - Mention related context keys
   - Link to complementary patterns

## 🔍 Finding Context Later

### Quick Retrieval
- Get specific context: pop_context("user-auth-jwt-pattern")
- Search by topic: list_contexts(tag="authentication")
- Semantic search: search_contexts("JWT token management")

### Discovery
- See all available contexts: list_contexts()
- Get project overview: analyze_project_context()
- Find next tasks: suggest_next_actions()

## 💡 Pro Tips

1. **Be Specific but Searchable**
   - Good: "react-component-error-boundaries"
   - Avoid: "error-stuff" or "component-thing"

2. **Include the 'Why' Not Just the 'What'**
   - Explain reasoning behind decisions
   - Note alternatives considered and rejected

3. **Update Over Time**
   - Contexts can evolve with your codebase
   - Update when patterns change or improve

4. **Cross-Reference Heavily**
   - Link related contexts together
   - Build a knowledge graph of your decisions

5. **Use Rich Formatting**
   - Code blocks with syntax highlighting
   - Clear headers and organization
   - Bullet points for quick scanning

---

**Remember:** The goal is to create context so rich that your future AI sessions can immediately understand and apply your project's patterns, decisions, and knowledge without lengthy explanations.

## 🚀 Getting Started

1. Use push_context() to store your first context
2. Try the assemble_context_guide prompt to see this guide
3. Use list_contexts() to see what you've stored
4. Use pop_context() to retrieve contexts in future sessions

The more rich context you store now, the more effective your future AI coding sessions will be!"""
    
    return guide_text


@mcp.prompt()
async def setup_context_guide() -> str:
    """
    Guide for creating comprehensive project setup and virtual environment context.
    
    This prompt helps you document everything needed to get a project running,
    including virtual environments, dependencies, configuration, and run instructions.
    """
    setup_guide = """# 🔧 Project Setup Context Guide

## Overview
Document everything a developer (or AI) needs to get your project running from scratch. This context is invaluable for onboarding, deployment, and resuming work after time away.

## 🎯 Essential Setup Information to Capture

### Environment Setup
- Virtual environment creation and activation
- Package/dependency management
- Environment variables and configuration
- Database setup and migrations
- Service dependencies (Redis, Docker, etc.)

### Development Workflow
- Build processes and commands
- Testing procedures
- Linting and formatting
- Development server startup
- Debugging setup

### Deployment Considerations
- Production environment differences
- Environment-specific configurations
- Deployment commands and procedures

## 📋 Step-by-Step Context Assembly

### 1. Virtual Environment Documentation

#### For Python Projects:
```
## Virtual Environment Setup

### Using venv (Python 3.3+)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt

### Using conda
conda create -n projectname python=3.11
conda activate projectname
pip install -r requirements.txt

### Using uv (modern Python package manager)
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
uv pip install -r requirements.txt

### Development Dependencies
pip install -r requirements-dev.txt  # If separate dev requirements
```

#### For Node.js Projects:
```
## Node Environment Setup

### Using npm
npm install
npm run dev

### Using yarn
yarn install
yarn dev

### Using pnpm
pnpm install
pnpm dev

### Node Version Management
nvm use 18  # Or whatever version specified in .nvmrc
```

### 2. Configuration Documentation

```
## Environment Configuration

### Required Environment Variables
- DATABASE_URL: Connection string for main database
- REDIS_URL: Redis connection for caching
- API_KEY: Third-party service API key
- DEBUG: Set to 'true' for development

### Configuration Files
- .env.example: Template for environment variables
- config/settings.py: Main configuration module
- docker-compose.yml: Local development services

### Database Setup
# First time setup
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json
```

### 3. Service Dependencies

```
## External Services

### Database
- PostgreSQL 14+ required
- Create database: createdb projectname
- Run migrations: python manage.py migrate

### Cache/Queue
- Redis for caching and background jobs
- Start with Docker: docker run -d -p 6379:6379 redis

### File Storage
- AWS S3 for production
- Local filesystem for development
- Configure in settings based on environment
```

## 🛠️ Complete Setup Context Template

```markdown
# [Project Name] Setup Instructions

## Quick Start
[One-command setup if possible, e.g., make install && make run]

## Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend assets)

## Environment Setup

### 1. Clone and Navigate
git clone [repository-url]
cd [project-directory]

### 2. Virtual Environment
[Specific commands for your project]

### 3. Dependencies
[Installation commands]

### 4. Configuration
cp .env.example .env
# Edit .env with your local settings

### 5. Database
[Database setup commands]

### 6. Initial Data
[Any seed data or initial setup]

## Development Commands

### Start Development Server
[Command to start local server]

### Run Tests
[Test execution commands]

### Database Operations
[Migration, backup, restore commands]

### Build/Deploy
[Production build commands]

## Troubleshooting

### Common Issues
- [Issue 1]: [Solution]
- [Issue 2]: [Solution]

### Port Conflicts
[How to handle common port issues]

### Permission Issues
[Platform-specific permission fixes]

## IDE/Editor Setup
- [Recommended extensions]
- [Debugger configuration]
- [Code formatting setup]

## Platform-Specific Notes

### macOS
[Any macOS-specific requirements]

### Windows
[Windows-specific setup steps]

### Linux
[Linux distribution considerations]
```

## 📝 Practical Examples

### Example 1: Django Web Application
```
Key: "django-project-setup"
Tags: ["setup", "django", "python", "environment", "database"]
Priority: "high"

Content should include:
- Virtual environment with specific Python version
- PostgreSQL database creation
- Environment variables for Django settings
- Static file collection
- Migration commands
- Superuser creation
- Development server startup
- Common troubleshooting steps
```

### Example 2: React + Node.js Full Stack
```
Key: "fullstack-dev-environment"
Tags: ["setup", "react", "nodejs", "fullstack", "environment"]
Priority: "high"

Content should include:
- Node version requirements
- Package manager choice (npm/yarn/pnpm)
- Environment variables for both frontend and backend
- Database setup (if applicable)
- Concurrent development server startup
- Build process for production
- Port configuration
```

### Example 3: Microservices with Docker
```
Key: "microservices-docker-setup"
Tags: ["setup", "docker", "microservices", "environment"]
Priority: "high"

Content should include:
- Docker and Docker Compose installation
- Service orchestration with docker-compose
- Environment variable management
- Volume mounting for development
- Log aggregation setup
- Service health checks
- Local vs production differences
```

## 🚀 Context Storage Best Practices

### 1. Be Comprehensive but Concise
- Include all necessary steps
- Avoid overwhelming detail
- Use clear, copy-pastable commands

### 2. Test Your Instructions
- Follow your own setup guide on a fresh machine
- Update when processes change
- Include timing expectations ("This step takes ~5 minutes")

### 3. Include Troubleshooting
- Document common error messages
- Provide solutions for typical issues
- Include platform-specific gotchas

### 4. Version Information
- Specify required versions for dependencies
- Note when versions are critical vs flexible
- Include upgrade/downgrade procedures

### 5. Security Considerations
- Never include actual secrets or API keys
- Document which environment variables need real values
- Include instructions for obtaining necessary credentials

## 💡 Pro Tips for Setup Context

1. **Start Fresh**: Test setup on a clean virtual machine or container
2. **Time Stamp**: Note when instructions were last verified
3. **Dependencies**: Document both direct and system dependencies
4. **Alternatives**: Include multiple approaches when applicable (pip vs conda, etc.)
5. **Automation**: Include any setup scripts or Makefiles
6. **Rollback**: Document how to clean up or start over

## 🔍 Using Setup Context

### Store the Context
```python
await push_context(
    key="project-setup-complete",
    content=setup_instructions,
    tags=["setup", "environment", "dependencies", "onboarding"],
    priority="high"
)
```

### Retrieve When Needed
```python
# Get setup instructions
setup = await pop_context("project-setup-complete")

# Find all setup-related contexts
setups = await list_contexts(tag="setup")
```

---

**Remember**: Good setup documentation saves hours of debugging and enables quick project recovery. Update this context whenever your setup process changes!"""
    
    return setup_guide


if __name__ == "__main__":
    # Start backend if needed
    start_backend()
    
    # Run the MCP server
    mcp.run()