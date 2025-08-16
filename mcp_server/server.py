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


if __name__ == "__main__":
    # Start backend if needed
    start_backend()
    
    # Run the MCP server
    mcp.run()