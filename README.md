# AI Travel Planning System

A production-quality multi-agent AI travel planning platform built with **LangGraph**, **FastAPI**, **Groq (LLaMA 3.3)**, and a modern **HTML/CSS/JavaScript** frontend.

![Architecture](docs/screenshots/architecture.png)

> Screenshot placeholders — add your own screenshots to `docs/screenshots/`.

---

## Features

- **Supervisor-led multi-agent pipeline** — routes requests to only the agents you need
- **Parallel specialist agents** — Flight, Hotel, Budget, Attraction, Travel Tips
- **Critic + Reflection** — self-correction with confidence scoring
- **PostgreSQL memory** — conversation summaries and preference learning
- **REST API** — full CRUD for trips, preferences, analytics, exports
- **Modern responsive UI** — dark mode, toasts, modals, trip cards, history
- **Export** — JSON, Markdown, clipboard copy
- **Compare plans** — side-by-side confidence comparison

---

## Architecture

```
User → FastAPI → TravelService → LangGraph
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Validate State   Memory Retrieval   Supervisor
                    │               │               │
                    └───────────────┴───────────────┘
                                    ▼
                          Parallel Executor
                    (Flight / Hotel / Budget / Attraction / Tips)
                                    ▼
                          Error Recovery → Critic
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                   Reflection            Response Formatter
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                          PostgreSQL + Trip Record
```

---

## Folder Structure

```
app/
├── agents/          # LangGraph agent nodes
├── graph/           # State, routing, builder, visualization
├── tools/           # LangChain tools (Flight, Hotel, Tavily-based)
├── services/        # Business logic layer
├── database/        # SQLAlchemy models, repositories
├── memory/          # Checkpointing, conversation summaries
├── schemas/         # Pydantic request/response models
├── prompts/         # Agent prompt templates
├── routers/         # FastAPI route handlers
├── middleware/      # Logging, rate limiting
├── static/          # CSS, JS, images
├── templates/       # Jinja2 HTML pages
├── utils/           # LLM, cache, retry, exceptions
├── config/          # Settings from environment
├── tests/           # Pytest tests
└── main.py          # FastAPI entry point
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/plan-trip` | Generate a full travel plan |
| `POST` | `/api/chat` | Chat-style trip planning |
| `POST` | `/api/plan-trip/stream` | SSE streaming pipeline |
| `GET` | `/api/history` | Trip history for user |
| `GET` | `/api/trip/{id}` | Trip detail |
| `DELETE` | `/api/history/{id}` | Delete a trip |
| `GET` | `/api/saved` | Favourite trips |
| `POST` | `/api/trip/{id}/favourite` | Toggle favourite |
| `GET` | `/api/trip/{id}/export/json` | Export as JSON |
| `GET` | `/api/trip/{id}/export/markdown` | Export as Markdown |
| `POST` | `/api/compare` | Compare two plans |
| `GET` | `/api/preferences` | Get user preferences |
| `POST` | `/api/preferences` | Update preferences |
| `GET` | `/api/analytics` | Usage analytics |

### Pages

| URL | Page |
|-----|------|
| `/` | Home |
| `/planner` | Trip Planner |
| `/history-page` | Trip History |
| `/saved-page` | Saved Trips |
| `/settings-page` | Settings |
| `/about` | About |

---

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- API keys: Groq, Tavily, AviationStack

### Setup

```bash
# 1. Clone and enter project
cd MULTIAGENT

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create PostgreSQL database
# CREATE DATABASE langgraph_memory_db;

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys and DATABASE_URL

# 6. Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

### Environment Variables

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
AVIATIONSTACK_API_KEY=your_aviationstack_key
DATABASE_URL=postgresql://postgres:root@localhost:5432/langgraph_memory_db
```

---

## How LangGraph Works

1. **Validate** — ensures all state fields have defaults
2. **Memory Retrieval** — loads user preferences and past conversation summaries from PostgreSQL
3. **Supervisor** — LLM decides which agents to activate (e.g., only Flight for "find flights to Tokyo")
4. **Parallel Executor** — runs selected agents concurrently via ThreadPoolExecutor
5. **Itinerary Generation** — LLM builds day-by-day plan from collected data
6. **Critic** — reviews quality, assigns confidence score (0–1)
7. **Reflection** (conditional) — if confidence < 0.7, self-corrects the plan
8. **Response Formatter** — produces markdown plan + structured JSON with checklists

Conditional edges:
- Supervisor → always routes to parallel executor (agents filtered by supervisor)
- Critic → reflection if `needs_reflection && retry_count < 2 && confidence < 0.7`

---

## How Memory Works

Instead of storing every chat message:

1. After each trip, an LLM generates a **conversation summary** (destinations, topics, preferences)
2. Summary is stored in `conversation_summaries` table
3. User preferences (airline, hotel type, travel style, budget) are updated in `user_preferences`
4. On next request, `retrieve_memories()` builds a context string injected into the graph
5. LangGraph **checkpointing** (PostgresSaver) persists graph state per thread

---

## Running Tests

```bash
pytest app/tests/ -v
```

---

## Legacy Entry Points

The original Streamlit UI and linear 4-agent graph are preserved for backward compatibility:

```bash
# Old LangGraph CLI
python main.py

# Old Streamlit UI
streamlit run frontend.py
```

---

## Future Improvements

- [ ] Real-time SSE streaming in the frontend planner
- [ ] Dedicated hotel/flight APIs (replace Tavily wrappers)
- [ ] User authentication (JWT)
- [ ] Redis caching layer
- [ ] Docker Compose deployment
- [ ] Graph visualization endpoint (`/api/graph`)
- [ ] Multi-language support
- [ ] Mobile PWA

---

## Resume Description

> Built a production AI Travel Planning Platform using LangGraph multi-agent orchestration with supervisor routing, parallel specialist agents, critic/reflection self-correction, and PostgreSQL long-term memory. Developed FastAPI REST backend with SQLAlchemy ORM, repository pattern, Pydantic validation, rate limiting, and conversation summary-based preference learning. Created responsive HTML/CSS/JS frontend with dark mode, trip history, exports, and plan comparison. Integrated Groq LLaMA, Tavily Search, and AviationStack APIs.

---

## License

MIT
