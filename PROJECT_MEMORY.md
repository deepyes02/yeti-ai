# Yeti AI Agent - Project Memory & Configuration Guide

**Last Updated:** 2026-01-04  
**Project Path:** `/Users/deepesh/Desktop/github-projects/ai-agent`

---

## 📋 Project Overview

**Yeti** is a full-stack AI agent application powered by Mistral-Nemo running locally via `llama_cpp`. It provides a conversational AI interface with tool-calling capabilities for weather, exchange rates, web search, and datetime queries.

### Architecture
- **Inference:** Local `llama-server` running on host OS (MacBook Pro M2)
- **Backend:** FastAPI (Python 3.11) in Docker
- **Frontend:** Next.js (React) in Docker  
- **Database:** PostgreSQL 15 in Docker
- **Agent Framework:** LangChain + LangGraph (ReAct pattern)

---

## 🔧 Environment Configuration

### Virtual Environment
- **Path:** `./env`
- **Python Version:** 3.11
- **Purpose:** Local testing of scripts only (NOT used by Docker)
- **Status File:** `.venv_status` (tracks activation state)

### Environment Variables (.env)

Based on `.env.sample`, required variables:

```bash
# LangSmith (Optional - for debugging/tracing)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="your_api_key_here"
LANGSMITH_PROJECT="yeti-ai"

# Database (Required)
POSTGRESQL_URL="postgresql://deepyes02:yEti-2025-yAk-ai@db:5432/ai_agent"

# Legacy (Not used - kept for reference)
OLLAMA_BASE_URL="http://host.docker.internal:11434"
```

**Note:** The actual `.env` file is gitignored for security.

---

## 🚀 Running the Application

### Complete Reset (Recommended)
```bash
./flush-yeti.sh
```
This script:
1. Stops containers and cleans database volumes
2. Starts fresh Docker environment
3. Checks virtual environment status
4. Manages llama-server (kills old, starts new)

### Manual Steps

**1. Start LLM Server (Host OS):**
```bash
./run_ai_server.sh
# Or manually:
llama-server -m ~/Desktop/bin/llms/mistral-nemo-15.gguf --jinja -c 4096
```

**2. Start Docker Services:**
```bash
docker compose up -d
```

**3. Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database: postgresql://localhost:5432
- AI Server: http://localhost:8080
- PgAdmin: http://localhost:5050

---

## 🛠️ Development Workflow

### File Structure
```
/Users/deepesh/Desktop/github-projects/ai-agent/
├── app/                    # Backend Python code (mounted in Docker)
│   ├── main.py            # FastAPI entry point
│   ├── call_the_model.py  # Agent logic (CRITICAL - performance bottleneck)
│   └── utils/             # Tools, prompts, model loading
├── frontend/              # Next.js app (mounted in Docker)
│   └── src/               # React components
├── scripts/               # Local testing scripts (20+ files)
│   ├── tool_calling.py    # Test tool calling
│   ├── stream.py          # Test streaming
│   └── *.ipynb            # Jupyter notebooks for experiments
├── docker-compose.yml     # Multi-container setup
├── Dockerfile             # Backend container
├── requirements.txt       # Python dependencies
├── flush-yeti.sh          # Environment reset script ⭐
└── run_ai_server.sh       # LLM server startup
```

### Docker Containers
| Service | Container Name | Ports | Purpose |
|---------|---------------|-------|---------|
| Backend | `backend` | 8000 | FastAPI server |
| Frontend | `frontend` | 3000 | Next.js server |
| Database | `db` | 5432 | PostgreSQL |
| PgAdmin | `pgadmin` | 5050 | DB admin UI |

### Hot Reload
- **Backend:** Code changes in `./app` auto-reload (volume mount)
- **Frontend:** Code changes in `./frontend` auto-reload (npm dev mode)
- **After changes:** Run `docker compose restart backend` to apply

---

## 🐛 Known Issues & Current Work

### Performance Problem (28-Second Response Time)
**Status:** INVESTIGATING  
**Root Cause:** `create_react_agent` makes 4-5 POST requests per prompt  
**Location:** `app/call_the_model.py:49-51`

**Problem:**
```python
# This runs on EVERY request - very expensive!
async with AsyncPostgresSaver.from_conn_string(conn) as checkpointer:
    await checkpointer.setup()  # DB setup overhead
    app = create_react_agent(model, tools, checkpointer=checkpointer)  # Agent recreation
```

**Observation:**
- User sees 4-5 LLM invocations per simple query
- Each invocation: ~5-7 seconds
- Total: 28 seconds for simple responses

**Previous Fast Version:** Commit `2d3bf9c` used manual graph construction with global agent initialization

---

## 🧪 Testing

### Local Script Testing
```bash
source ./env/bin/activate  # IMPORTANT: Always activate first!
python scripts/tool_calling.py
python scripts/stream.py
```

### Docker Testing
```bash
# View logs
docker logs -f backend
docker logs -f frontend

# Restart after changes
docker compose restart backend

# Full reset
./flush-yeti.sh
```

---

## 📦 Key Dependencies

### Backend (Python)
- `fastapi` - Web framework
- `langchain-core` - LLM abstraction
- `langgraph` - Agent orchestration
- `langchain-openai` - OpenAI-compatible wrapper
- `psycopg` - PostgreSQL adapter
- `langgraph-checkpoint-postgres` - State persistence

### Frontend (Node.js)
- `next` - React framework
- `react` - UI library
- WebSocket client for real-time streaming

---

## 🔑 Critical Files to Monitor

1. **`app/call_the_model.py`** - Agent logic (currently slow)
2. **`app/utils/system_prompt.py`** - Yeti's personality
3. **`app/main.py`** - WebSocket endpoint
4. **`docker-compose.yml`** - Service orchestration
5. **`.env`** - Environment secrets (gitignored)

---

## 📝 Common Commands

```bash
# Full environment reset
./flush-yeti.sh

# View backend logs with follow
docker logs -f backend

# Check container status
docker compose ps

# Stop everything (Docker + AI server)
docker compose down && pkill -f llama-server

# Rebuild containers
docker compose up -d --build

# Access Django-like shell (not applicable - FastAPI)
docker exec -it backend bash

# Check virtual environment before testing
if [ -f .venv_status ]; then cat .venv_status; fi
```

---

## 🎯 Next Steps (from current investigation)

1. ✅ Added detailed logging to track agent calls
2. ⏳ Test with sample queries to confirm 4-5 invocations
3. ⏳ Implement global agent initialization (like commit `2d3bf9c`)
4. ⏳ Verify performance improvement (target: <5s for simple queries)

---

## 💡 Development Tips

- **Always activate venv** before running local scripts
- **Check `flush-yeti.sh`** creates `.venv_status` to track this
- **Docker mounts code** - changes apply immediately (restart if needed)
- **llama-server logs** go to `llama_server.log`
- **Frontend errors** check browser console + `docker logs frontend`

---

_This memory file is auto-generated and should be updated as the project evolves._
