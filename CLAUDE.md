# Job Market Trend Analyzer

## Project Overview

A full-stack tool that pulls live job listings from the Adzuna API, extracts trending skills using NLP (spaCy), visualizes trends on an interactive dashboard (Recharts), and analyzes résumé skill gaps using the Anthropic API.

## Architecture

```
┌─────────────────┐        ┌──────────────────────────┐
│  React Frontend  │◄──────►│   FastAPI Backend         │
│  (Vite + Recharts)│       │   (Python 3.11+)          │
└─────────────────┘        │                            │
                            │  ┌──────────┐             │
                            │  │  SQLite  │             │
                            │  │ (via     │             │
                            │  │ SQLAlch.)│             │
                            │  └──────────┘             │
                            │                            │
                            │  External APIs:            │
                            │  • Adzuna (job listings)   │
                            │  • Anthropic (skills gap)  │
                            │  • spaCy (local NLP)       │
                            └──────────────────────────┘
```

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | FastAPI, Python 3.11+, SQLAlchemy, SQLite        |
| NLP        | Regex-based skill matcher (stdlib `re`, no deps)|
| Frontend   | React 18, Vite, Recharts, Axios                 |
| AI / LLM   | Anthropic API (claude-sonnet-4-6)               |
| Job Data   | Adzuna Public API                               |

## Repository Layout

```
Job-Market-Analyzer/
├── CLAUDE.md
├── .env.example               # Template for required env vars
├── .gitignore
│
├── backend/
│   ├── main.py                # FastAPI app entry point
│   ├── database.py            # SQLAlchemy engine + session
│   ├── requirements.txt
│   │
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── job.py             # Job listing model
│   │   └── skill.py           # Skill trend model
│   │
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── job.py
│   │   └── skill.py
│   │
│   ├── routers/               # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── jobs.py            # GET /jobs — fetch & store listings
│   │   ├── skills.py          # GET /skills/trending
│   │   └── resume.py          # POST /resume/analyze
│   │
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── adzuna.py          # Adzuna API client
│   │   ├── nlp.py             # spaCy skill extraction
│   │   └── anthropic_client.py# Anthropic résumé gap analysis
│   │
│   └── data/                  # SQLite DB file lives here (gitignored)
│       └── .gitkeep
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    │
    └── src/
        ├── main.jsx           # React entry point
        ├── App.jsx            # Root component + routing
        │
        ├── components/
        │   ├── Dashboard.jsx        # Main dashboard layout
        │   ├── SkillsBarChart.jsx   # Top N trending skills bar chart
        │   ├── TrendLineChart.jsx   # Skill frequency over time
        │   ├── JobList.jsx          # Paginated job listing table
        │   └── ResumeAnalyzer.jsx   # Résumé upload + gap report
        │
        ├── services/
        │   └── api.js         # Axios instance + API helpers
        │
        └── styles/
            └── index.css
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable                | Description                              |
|-------------------------|------------------------------------------|
| `ADZUNA_APP_ID`         | Adzuna API application ID                |
| `ADZUNA_APP_KEY`        | Adzuna API application key               |
| `ANTHROPIC_API_KEY`     | Anthropic API key                        |
| `DATABASE_URL`          | SQLite path, e.g. `sqlite:///data/jobs.db` |
| `VITE_API_BASE_URL`     | Backend URL seen by the browser, e.g. `http://localhost:8000` |

## Key Commands

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run dev server (auto-reload)
uvicorn main:app --reload --port 8000

# Interactive API docs
open http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # Vite dev server on http://localhost:5173
npm run build      # Production build → dist/
npm run preview    # Preview production build locally
```

## API Endpoints (planned)

| Method | Path                  | Description                              |
|--------|-----------------------|------------------------------------------|
| GET    | `/jobs/fetch`         | Pull latest listings from Adzuna         |
| GET    | `/jobs`               | List stored job listings (paginated)     |
| GET    | `/skills/trending`    | Top N skills with frequency counts       |
| GET    | `/skills/history`     | Skill frequency over time (for charts)   |
| POST   | `/resume/analyze`     | Upload résumé text → Anthropic gap report|

## Data Flow

1. **Ingest** — `/jobs/fetch` calls Adzuna, stores raw listings in SQLite.
2. **Extract** — NLP service passes job descriptions through spaCy to identify skill tokens/entities; results written to the `skills` table.
3. **Aggregate** — `/skills/trending` queries the DB and returns ranked skill counts.
4. **Visualize** — Frontend polls the API and renders Recharts bar/line charts.
5. **Analyze** — User pastes résumé text; backend sends it + trending skills to Anthropic, returns a structured gap report.

## Development Notes

- SQLite DB is auto-created on first backend startup via `Base.metadata.create_all()`
- Adzuna free tier allows ~100 req/day — cache aggressively; avoid re-fetching on every request
- Keep Anthropic calls in `services/anthropic_client.py` to make model/prompt swaps easy
- Use `claude-sonnet-4-6` as the default model for résumé analysis
