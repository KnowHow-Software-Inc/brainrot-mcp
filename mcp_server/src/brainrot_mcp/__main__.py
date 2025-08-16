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
    tags: Optional[List[str]] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Push (store) context from the current session for later retrieval.
    
    This tool captures important context like architecture decisions, code patterns,
    TODOs, or any other information you want to persist between sessions.
    
    Args:
        key: Unique identifier for this context (e.g., "auth-pattern", "todo-refactor-api")
        content: The full context to store
        tags: List of tags for categorization (e.g., ["architecture", "security"])
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
        
        # Process tags - handle potential JSON string from MCP framework
        parsed_tags = []
        
        # Debug logging to file
        import os
        debug_path = "/tmp/mcp_tags_debug.log"
        with open(debug_path, "a") as f:
            f.write(f"\n--- New Request ---\n")
            f.write(f"tags type: {type(tags)}\n")
            f.write(f"tags value: {repr(tags)}\n")
            f.write(f"tags is str: {isinstance(tags, str)}\n")
            f.write(f"tags is list: {isinstance(tags, list)}\n")
        
        if tags:
            # Check if tags is actually a string (MCP framework issue)
            if isinstance(tags, str):
                # It's a JSON-encoded string, parse it
                if tags.strip().startswith('[') and tags.strip().endswith(']'):
                    try:
                        import json
                        parsed_tags = json.loads(tags)
                        parsed_tags = [str(tag).strip() for tag in parsed_tags if str(tag).strip()]
                    except json.JSONDecodeError:
                        # Fallback: treat as single tag
                        parsed_tags = [tags.strip()] if tags.strip() else []
                else:
                    # Single tag as string
                    parsed_tags = [tags.strip()] if tags.strip() else []
            elif isinstance(tags, list):
                # Proper list received
                parsed_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
        
        # Log the parsed result
        with open(debug_path, "a") as f:
            f.write(f"parsed_tags: {repr(parsed_tags)}\n")
        
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
        contexts_result = await list_contexts(limit=50)
        if not contexts_result.get("success"):
            return "Error retrieving contexts: " + contexts_result.get("error", "Unknown error")
        
        contexts = contexts_result.get("contexts", [])
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
        high_priority = [ctx for ctx in contexts if ctx.get("priority") == "high"]
        if high_priority:
            analysis.append("## 🚨 High Priority Items")
            for ctx in high_priority:
                analysis.append(f"- **{ctx['key']}**: {ctx['summary']}")
                analysis.append(f"  Tags: {', '.join(ctx.get('tags', []))}")
            analysis.append("")
        
        # By category
        for tag, items in sorted(by_tag.items()):
            if tag == "untagged":
                continue
            analysis.append(f"## {tag.upper()} ({len(items)} items)")
            for ctx in items[:3]:  # Show first 3
                analysis.append(f"- **{ctx['key']}**: {ctx['summary']}")
            if len(items) > 3:
                analysis.append(f"  ... and {len(items) - 3} more")
            analysis.append("")
        
        return "\n".join(analysis)
        
    except Exception as e:
        return f"Error analyzing project context: {str(e)}"


@mcp.prompt()
async def suggest_next_actions() -> str:
    """
    Suggest next actions based on stored TODOs and technical debt.
    
    This prompt reviews stored contexts to prioritize what should be worked on next.
    """
    try:
        # Get TODO and tech debt contexts
        todo_result = await list_contexts(tag="todo", limit=20)
        debt_result = await list_contexts(tag="tech-debt", limit=20)
        
        suggestions = ["# Suggested Next Actions\n"]
        
        # High priority TODOs
        if todo_result.get("success"):
            todos = todo_result.get("contexts", [])
            high_priority_todos = [t for t in todos if t.get("priority") == "high"]
            
            if high_priority_todos:
                suggestions.append("## 🔥 Immediate Actions (High Priority TODOs)")
                for todo in high_priority_todos:
                    suggestions.append(f"1. **{todo['key']}**: {todo['summary']}")
                suggestions.append("")
        
        # Technical debt opportunities
        if debt_result.get("success"):
            debts = debt_result.get("contexts", [])
            if debts:
                suggestions.append("## 🔧 Technical Debt to Address")
                for debt in debts[:3]:
                    suggestions.append(f"- **{debt['key']}**: {debt['summary']}")
                suggestions.append("")
        
        # Regular TODOs
        if todo_result.get("success"):
            todos = todo_result.get("contexts", [])
            regular_todos = [t for t in todos if t.get("priority") != "high"]
            
            if regular_todos:
                suggestions.append("## 📝 Other TODOs")
                for todo in regular_todos[:5]:
                    priority = todo.get("priority", "medium")
                    suggestions.append(f"- **{todo['key']}** ({priority}): {todo['summary']}")
                suggestions.append("")
        
        if len(suggestions) == 1:  # Only header
            suggestions.append("No TODOs or technical debt found.")
            suggestions.append("Consider using push_context() to track tasks and improvements.")
        
        return "\n".join(suggestions)
        
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
        # Get all contexts
        all_contexts = await list_contexts(limit=100)
        if not all_contexts.get("success"):
            return f"Error retrieving contexts: {all_contexts.get('error', 'Unknown error')}"
        
        contexts = all_contexts.get("contexts", [])
        if not contexts:
            return "No stored contexts found. Consider storing architectural decisions and patterns first."
        
        # Search for relevant contexts (simple keyword matching)
        feature_keywords = feature_name.lower().split()
        relevant_contexts = []
        
        for ctx in contexts:
            content_lower = (ctx.get("summary", "") + " " + ctx.get("key", "")).lower()
            if any(keyword in content_lower for keyword in feature_keywords):
                relevant_contexts.append(ctx)
        
        response = [f"# Context for Feature: {feature_name}\n"]
        
        if relevant_contexts:
            response.append("## 🎯 Directly Relevant Contexts")
            for ctx in relevant_contexts:
                response.append(f"- **{ctx['key']}**: {ctx['summary']}")
                response.append(f"  Tags: {', '.join(ctx.get('tags', []))}")
            response.append("")
        
        # Always show architecture and security contexts
        arch_contexts = [ctx for ctx in contexts if "architecture" in ctx.get("tags", [])]
        if arch_contexts:
            response.append("## 📐 Architecture Decisions to Consider")
            for ctx in arch_contexts[:3]:
                response.append(f"- **{ctx['key']}**: {ctx['summary']}")
            response.append("")
        
        security_contexts = [ctx for ctx in contexts if "security" in ctx.get("tags", [])]
        if security_contexts:
            response.append("## 🔒 Security Considerations")
            for ctx in security_contexts[:3]:
                response.append(f"- **{ctx['key']}**: {ctx['summary']}")
            response.append("")
        
        if not relevant_contexts and not arch_contexts and not security_contexts:
            response.append("No directly relevant contexts found.")
            response.append("Consider reviewing all stored contexts or adding feature-specific context.")
        
        return "\n".join(response)
        
    except Exception as e:
        return f"Error getting context for feature: {str(e)}"


if __name__ == "__main__":
    # Start backend if needed
    start_backend()
    
    # Run the MCP server
    mcp.run()