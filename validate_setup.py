#!/usr/bin/env python3
"""
Brainrot MCP Setup Validation Script

This script validates that your Brainrot MCP setup is working correctly.
Run this after following the setup instructions in SETUP.md
"""

import os
import sys
import json
import subprocess
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, status: str = "info"):
    """Print colored status messages"""
    if status == "success":
        print(f"{Colors.GREEN}✓{Colors.END} {message}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.END} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def run_command(cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=10
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def check_python_version() -> bool:
    """Check if Python version is 3.12+"""
    print_status("Checking Python version...", "info")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.12+", "error")
        return False

def check_uv_installation() -> bool:
    """Check if uv is installed"""
    print_status("Checking uv installation...", "info")
    
    success, output = run_command(["uv", "--version"])
    if success:
        print_status(f"uv installed: {output.strip()}", "success")
        return True
    else:
        print_status("uv not found - install from https://docs.astral.sh/uv/", "warning")
        return False

def check_project_structure() -> bool:
    """Check if project structure is correct"""
    print_status("Checking project structure...", "info")
    
    required_files = [
        "backend/server.py",
        "backend/requirements.txt",
        "mcp_server/server.py", 
        "mcp_server/pyproject.toml",
        "CLAUDE.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print_status(f"Missing files: {', '.join(missing_files)}", "error")
        return False
    else:
        print_status("Project structure ✓", "success")
        return True

def check_backend_dependencies() -> bool:
    """Check if backend dependencies are installed"""
    print_status("Checking backend dependencies...", "info")
    
    # Check if virtual environment exists
    backend_venv = Path("backend/.venv")
    if not backend_venv.exists():
        print_status("Backend virtual environment not found", "error")
        return False
    
    # Try to run a simple import test
    success, output = run_command([
        "uv", "run", "python", "-c", 
        "import fastapi, uvicorn, sqlalchemy, pydantic; print('All imports successful')"
    ], cwd="backend")
    
    if success:
        print_status("Backend dependencies ✓", "success")
        return True
    else:
        print_status(f"Backend dependency issues: {output}", "error")
        return False

def check_mcp_dependencies() -> bool:
    """Check if MCP server dependencies are installed"""
    print_status("Checking MCP server dependencies...", "info")
    
    # Check if virtual environment exists
    mcp_venv = Path("mcp_server/.venv")
    if not mcp_venv.exists():
        print_status("MCP server virtual environment not found", "error")
        return False
    
    # Try to run a simple import test
    success, output = run_command([
        "uv", "run", "python", "-c", 
        "import fastmcp, httpx; print('All imports successful')"
    ], cwd="mcp_server")
    
    if success:
        print_status("MCP server dependencies ✓", "success")
        return True
    else:
        print_status(f"MCP dependency issues: {output}", "error")
        return False

def check_backend_server() -> bool:
    """Check if backend server can start and respond"""
    print_status("Testing backend server...", "info")
    
    # Try to connect to backend
    try:
        response = requests.get("http://localhost:8000/api/contexts", timeout=5)
        if response.status_code == 200:
            print_status("Backend server is running ✓", "success")
            return True
        else:
            print_status(f"Backend server responded with status {response.status_code}", "warning")
            return False
    except requests.exceptions.ConnectionError:
        print_status("Backend server not running - start with: cd backend && uv run python server.py", "warning")
        return False
    except requests.exceptions.Timeout:
        print_status("Backend server timeout", "error")
        return False

def check_mcp_server() -> bool:
    """Check if MCP server can be imported"""
    print_status("Testing MCP server import...", "info")
    
    success, output = run_command([
        "uv", "run", "python", "-c", 
        "import server; print('MCP server imports successfully')"
    ], cwd="mcp_server")
    
    if success:
        print_status("MCP server imports ✓", "success")
        return True
    else:
        print_status(f"MCP server import failed: {output}", "error")
        return False

def check_claude_config() -> bool:
    """Check Claude Desktop configuration"""
    print_status("Checking Claude Desktop configuration...", "info")
    
    # Common Claude config locations
    config_paths = [
        Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",  # macOS
        Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json",  # Windows
        Path.home() / ".config/claude/claude_desktop_config.json",  # Linux
    ]
    
    config_found = False
    for config_path in config_paths:
        if config_path.exists():
            config_found = True
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if "mcpServers" in config and "brainrot" in config["mcpServers"]:
                    brainrot_config = config["mcpServers"]["brainrot"]
                    print_status(f"Claude config found at {config_path}", "success")
                    print_status(f"Brainrot MCP configured ✓", "success")
                    
                    # Check if path exists
                    if "args" in brainrot_config and len(brainrot_config["args"]) > 2:
                        server_path = brainrot_config["args"][2]
                        if Path(server_path).exists():
                            print_status(f"MCP server path valid ✓", "success")
                        else:
                            print_status(f"MCP server path not found: {server_path}", "error")
                            return False
                    
                    return True
                else:
                    print_status(f"Claude config found but brainrot MCP not configured", "warning")
                    return False
            except json.JSONDecodeError:
                print_status(f"Claude config file is invalid JSON", "error")
                return False
            except Exception as e:
                print_status(f"Error reading Claude config: {e}", "error")
                return False
    
    if not config_found:
        print_status("Claude Desktop config not found", "warning")
        print_status("Create config file as described in SETUP.md", "info")
        return False

def print_summary(results: Dict[str, bool]):
    """Print validation summary"""
    print(f"\n{Colors.BOLD}=== VALIDATION SUMMARY ==={Colors.END}")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    for check, passed in results.items():
        status = "success" if passed else "error"
        print_status(f"{check}: {'PASS' if passed else 'FAIL'}", status)
    
    print(f"\n{Colors.BOLD}Result: {passed_checks}/{total_checks} checks passed{Colors.END}")
    
    if passed_checks == total_checks:
        print_status("🎉 All checks passed! Your setup is ready.", "success")
        print_status("Try using the MCP tools in Claude Desktop:", "info")
        print("   /mcp list_contexts")
        print("   push_context('test', 'Hello from brainrot!')")
    else:
        print_status("❌ Some checks failed. Review the errors above.", "error")
        print_status("See SETUP.md for detailed setup instructions.", "info")

def main():
    """Run all validation checks"""
    print(f"{Colors.BOLD}Brainrot MCP Setup Validation{Colors.END}")
    print("=" * 40)
    
    # Define all checks
    checks = {
        "Python 3.12+": check_python_version,
        "UV Package Manager": check_uv_installation,
        "Project Structure": check_project_structure,
        "Backend Dependencies": check_backend_dependencies,
        "MCP Dependencies": check_mcp_dependencies,
        "Backend Server": check_backend_server,
        "MCP Server": check_mcp_server,
        "Claude Configuration": check_claude_config,
    }
    
    results = {}
    
    # Run each check
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_status(f"Error running {check_name}: {e}", "error")
            results[check_name] = False
        print()  # Add spacing between checks
    
    print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()