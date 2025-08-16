# Hackathon Agents and Commands for KnowHow MCP

## Core Hackathon Slash Commands

### Planning & Tracking
- `/hackathon-timer` - Track time against your 8-hour phases, alert when behind schedule
- `/checklist-sync` - Convert Hour 1-8 tasks into tracked todos, auto-update progress
- `/risk-check` - Quick assessment against your risk mitigation plan

### Rapid Development
- `/fastapi-scaffold` - Generate complete FastAPI structure with SQLite, CORS, Pydantic models
- `/mcp-tool` - Scaffold MCP tool with FastMCP, error handling, sanitization
- `/api-endpoint` - Generate REST endpoint with validation, error handling, docs

### Testing & Validation
- `/mcp-test` - Run MCP Inspector and validate tool responses
- `/demo-flow` - Test complete value loop (problem → request → response → solution)
- `/30sec-check` - Verify round-trip time meets your <30 second target

## Specialized Subagents

### 1. backend-builder
**Purpose:** Builds FastAPI backend following your exact spec
- SQLite schema from data model
- All 5 API endpoints with pagination
- CORS middleware configured
- Pydantic models matching JSON structure
- Auto-generates test data

### 2. mcp-implementer
**Purpose:** Handles MCP server implementation
- FastMCP setup with all 4 tools
- Context sanitization for secrets/tokens
- Backend API integration with httpx
- Rate limiting logic
- Comprehensive error handling

### 3. dashboard-creator
**Purpose:** Builds single-page dashboard
- Tailwind CSS from CDN
- Real-time updates every 30 seconds
- Filter by status/tech stack
- Mobile-responsive design
- Fallback to curl commands if breaks

### 4. demo-orchestrator
**Purpose:** Prepares and validates demo
- Seeds database with compelling examples
- Creates FastAPI project with CORS bug
- Pre-stages backup responses
- Validates 30-second flow
- Generates presenter notes

### 5. integration-validator
**Purpose:** End-to-end testing specialist
- Tests MCP → Backend → Dashboard flow
- Validates error handling at each layer
- Checks fallback mechanisms (JSON if SQLite fails)
- Performance testing for <30s round-trip

### 6. troubleshoot-mcp
**Purpose:** Rapid MCP debugging
- Analyzes MCP Inspector output
- Fixes FastMCP connection issues
- Validates tool registration
- Tests with mock requests
- Checks httpx async handling

## Quick-Action Commands

```bash
# Hour-specific accelerators
/hour1-setup     # Complete foundation in one command
/hour2-api       # Generate all endpoints
/hour3-mcp-core  # Build core MCP functionality
/hour5-dashboard # Create complete UI

# Emergency fixes
/fallback-json   # Switch from SQLite to JSON storage
/demo-backup     # Activate pre-staged responses
/cors-fix        # Apply standard CORS configuration
```

## Recommended Workflow

1. Start with `/checklist-sync` to load all tasks
2. Use `backend-builder` agent for Hour 1-2
3. Deploy `mcp-implementer` for Hour 3-4
4. Run `dashboard-creator` for Hour 5
5. Execute `integration-validator` for Hour 6
6. Activate `demo-orchestrator` for Hour 7
7. Keep `troubleshoot-mcp` ready throughout

## Implementation Notes

These agents and commands are designed to:
- Maximize velocity during the 8-hour hackathon
- Maintain clean architecture for demo
- Provide fallback options for common failures
- Ensure <30 second round-trip demonstration
- Support rapid pivoting if needed

Each agent should be configured with:
- Access to the PRD for context
- Ability to read/write all project directories
- Connection to test environments
- Error recovery capabilities