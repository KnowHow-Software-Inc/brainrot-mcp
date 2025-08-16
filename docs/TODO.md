# Brainrot MCP Implementation Plan

## 🎯 Goal: Complete working demo in 8 hours showing AI → Human → AI value loop

## ⏱️ Hour-by-Hour Execution Plan

### Hour 1: Foundation Setup (0-60 min)
- [ ] Initialize project structure
  - [ ] Create `backend/`, `mcp_server/`, `frontend/` directories
  - [ ] Set up Python virtual environments for backend and MCP
  - [ ] Create `.env` files with configuration
- [ ] Set up Backend API foundation
  - [ ] Initialize FastAPI with CORS middleware
  - [ ] Create SQLite database connection using DatabaseManager pattern from initial-scope.md
  - [ ] Define Pydantic models for help_requests and responses
- [ ] Verify basic connectivity
  - [ ] Test FastAPI runs on port 8000
  - [ ] Confirm SQLite database creates successfully

### Hour 2: Backend API Complete (60-120 min)
- [ ] Implement all 5 API endpoints
  - [ ] POST `/api/help-requests` - Create new help request
  - [ ] GET `/api/help-requests` - List all requests with pagination
  - [ ] GET `/api/help-requests/{id}` - Get specific request details
  - [ ] POST `/api/help-requests/{id}/responses` - Add response to request
  - [ ] GET `/api/dashboard-stats` - Get statistics for dashboard
- [ ] Add database schema
  - [ ] help_requests table (id, user_id, title, context, tech_stack, status, created_at)
  - [ ] responses table (id, request_id, responder_name, solution, created_at)
- [ ] Test with curl/httpie
  - [ ] Verify all endpoints return correct data
  - [ ] Test error handling for missing resources

### Hour 3: MCP Core Tools (120-180 min)
- [ ] Set up FastMCP server structure
  - [ ] Use server.py pattern from initial-scope.md lines 89-139
  - [ ] Configure with Brainrot-specific settings
- [ ] Implement `post_help_request` tool
  - [ ] Context sanitization for secrets/tokens
  - [ ] Integration with backend API using httpx
  - [ ] Return request ID for tracking
- [ ] Implement `check_responses` tool
  - [ ] Poll backend for responses to user's requests
  - [ ] Format responses for LLM consumption

### Hour 4: MCP Additional Tools (180-240 min)
- [ ] Implement `list_my_requests` tool
  - [ ] Filter by user_id from context
  - [ ] Show status and response count
- [ ] Implement `provide_help` tool
  - [ ] Allow responding to others' requests
  - [ ] Include responder identification
- [ ] Test with MCP Inspector
  - [ ] Run `npx @modelcontextprotocol/inspector python mcp_server/server.py`
  - [ ] Verify all 4 tools register and execute correctly
  - [ ] Test error handling and edge cases

### Hour 5: Dashboard UI (240-300 min)
- [ ] Create single-page dashboard (`frontend/index.html`)
  - [ ] Include Tailwind CSS from CDN
  - [ ] Fetch API integration with backend
  - [ ] Auto-refresh every 30 seconds
- [ ] Implement core features
  - [ ] List view of all help requests
  - [ ] Filter by status (pending/answered)
  - [ ] Click to view request details
  - [ ] Response form with syntax highlighting
- [ ] Mobile responsive design
  - [ ] Test on phone simulator
  - [ ] Ensure readable on small screens

### Hour 6: Integration Testing (300-360 min)
- [ ] End-to-end flow testing
  - [ ] Create help request via MCP → Verify in dashboard
  - [ ] Add response via dashboard → Check via MCP tool
  - [ ] Measure round-trip time (<30 seconds target)
- [ ] Error recovery testing
  - [ ] Test with backend down
  - [ ] Test with malformed requests
  - [ ] Verify graceful degradation
- [ ] Performance validation
  - [ ] Load test with 50+ requests
  - [ ] Verify dashboard remains responsive
  - [ ] Check database query performance

### Hour 7: Demo Preparation (360-420 min)
- [ ] Seed compelling demo data
  - [ ] FastAPI CORS configuration problem
  - [ ] React useEffect infinite loop issue
  - [ ] Docker container networking challenge
  - [ ] Pre-stage expert responses for each
- [ ] Create demo script
  - [ ] 2-minute problem setup
  - [ ] Show help request creation
  - [ ] Switch to dashboard, add response
  - [ ] Return to LLM, retrieve solution
  - [ ] Implement solution live
- [ ] Prepare backup plan
  - [ ] Screenshots of working flow
  - [ ] Pre-recorded video if live demo fails
  - [ ] JSON file fallback if SQLite fails

### Hour 8: Polish & Deploy (420-480 min)
- [ ] Fix critical bugs only
  - [ ] Focus on demo-breaking issues
  - [ ] Document known limitations
- [ ] Create README with setup instructions
  - [ ] Requirements and dependencies
  - [ ] Quick start commands
  - [ ] Architecture diagram
- [ ] Final demo run-through
  - [ ] Practice 3 times
  - [ ] Time each run (<5 minutes)
  - [ ] Refine talking points
- [ ] Package for submission
  - [ ] Clean up debug code
  - [ ] Remove test data except demo seeds
  - [ ] Final git commit

## 🚀 Quick Commands

```bash
# Backend setup & run
cd backend && python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn aiosqlite python-dotenv
python server.py

# MCP setup & test
cd mcp_server && python -m venv .venv && source .venv/bin/activate
pip install fastmcp httpx python-dotenv
npx @modelcontextprotocol/inspector python server.py

# Frontend serve
python -m http.server 8080 --directory frontend
```

## 🔥 Critical Success Factors

1. **30-second round trip** - Must demonstrate value loop quickly
2. **Context sanitization** - Remove any secrets/tokens before posting
3. **Graceful degradation** - System works even if parts fail
4. **Compelling demo** - Real problem → Real solution
5. **Clean architecture** - Judges can understand the code

## 🚨 Risk Mitigations

| Risk | Mitigation | Fallback |
|------|------------|----------|
| SQLite corruption | Test with small data first | Switch to JSON file storage |
| MCP connection fails | Use MCP Inspector throughout | Direct HTTP calls to backend |
| Dashboard breaks | Keep it simple, test often | Curl commands as backup |
| Demo fails live | Practice 3+ times | Pre-recorded video ready |
| Time runs out | Focus on core loop first | Document "future work" |

## 📊 Progress Tracking

- [ ] Hour 1 complete: Foundation running
- [ ] Hour 2 complete: All APIs working
- [ ] Hour 3 complete: 2 MCP tools working
- [ ] Hour 4 complete: All 4 MCP tools working
- [ ] Hour 5 complete: Dashboard functional
- [ ] Hour 6 complete: Integration tested
- [ ] Hour 7 complete: Demo ready
- [ ] Hour 8 complete: Submitted!

## 🎯 Definition of Done

- [ ] LLM can create help request via MCP tool
- [ ] Dashboard shows request within 30 seconds
- [ ] Human can respond via web interface
- [ ] LLM can retrieve response via MCP tool
- [ ] Complete cycle demonstrated in <5 minutes
- [ ] Code is clean and documented
- [ ] README explains architecture
- [ ] No critical bugs in demo flow

---

**Remember**: Perfect is the enemy of done. Focus on the core value loop working smoothly rather than adding features.