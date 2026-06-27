# Job Market Trend Analyzer

> Pull live job listings, extract trending skills with NLP, visualize demand on an interactive dashboard, and analyze your résumé against the market — all in one tool.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Recharts](https://img.shields.io/badge/Recharts-2.x-22B5BF?style=flat-square&logo=javascript&logoColor=white)](https://recharts.org)
[![Claude](https://img.shields.io/badge/Claude-Sonnet-D97706?style=flat-square)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-6B9E6B?style=flat-square)](LICENSE)

---

## Screenshots

**[Dashboard Screenshot]**

*Trending skills bar chart, daily frequency line chart, and paginated job listings.*

**[Resume Analyzer Screenshot]**

*Paste your résumé, get a match score, skills gap breakdown, and AI-generated action items.*

---

## Features

- **Real-time job data** — Fetches live listings from the [Adzuna API](https://developer.adzuna.com/) across any keyword and country. Fetch up to 500 jobs in a single click (10 pages × 50 results), with idempotent deduplication so re-fetching never creates duplicates.

- **Regex-based skill extraction** — A compiled regex matcher scans every job description for 60+ canonical tech skills (languages, frameworks, cloud, ML tooling, databases, and more) and writes them to SQLite for aggregation. Zero compiled dependencies — works on any platform.

- **Trending skills dashboard** — A horizontal bar chart ranks the top 15 skills by mention frequency. A line chart tracks how each skill's demand has changed day-over-day across multiple fetch sessions. Three stat cards give an at-a-glance summary.

- **Résumé gap analyzer** — Paste any résumé as plain text. The backend pulls the current top trending skills from the database and sends both to Claude Sonnet, which returns a structured JSON report: a match score (0–100), a plain-English summary, a split view of skills you already have vs. skills you need, and 3–5 concrete action items to close the gap.

- **Paginated job table** — Browse every stored listing with a client-side filter on title, company, and location. Click any title to open the original Adzuna posting.

- **Minimal, analytical UI** — Pastel sage, rose, and lavender palette on a warm off-white canvas. Shimmer skeleton screens on every loading path so the interface never feels blank.

---

## Built With

| Layer | Technology |
|---|---|
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com) + [Uvicorn](https://www.uvicorn.org) |
| **Database** | [SQLite](https://sqlite.org) via [SQLAlchemy 2.0](https://docs.sqlalchemy.org) (async) + [aiosqlite](https://github.com/omnilib/aiosqlite) |
| **Skill extraction** | Python `re` — compiled regex phrase matcher over a curated 60+ skill vocabulary |
| **Job data** | [Adzuna Public API](https://developer.adzuna.com/) |
| **AI analysis** | [Anthropic API](https://anthropic.com) — `claude-sonnet-4-6` |
| **Frontend** | [React 18](https://react.dev) + [Vite](https://vitejs.dev) |
| **Charts** | [Recharts](https://recharts.org) |
| **HTTP client** | [Axios](https://axios-http.com) (frontend) + [httpx](https://www.python-httpx.org) (backend) |
| **Settings** | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |

---

## How It Works

```
Adzuna API
    │
    ▼
GET /jobs/fetch  ──►  Store raw listings in SQLite (jobs table)
                           │
                           ▼
                    Regex skill matcher
                           │
                           ▼
                    Store skill rows (skills table)
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    GET /skills/trending        GET /skills/history
    (ranked skill counts)      (daily frequency over time)
              │                         │
              └────────────┬────────────┘
                           ▼
                    React Dashboard
                  (Recharts bar + line)

    POST /resume/analyze
         │
         ├── Pull top N trending skills from DB
         ├── Send résumé text + skills to Claude Sonnet
         └── Return: match score, gap breakdown, recommendations
```

1. **Ingest** — `GET /jobs/fetch` calls Adzuna for up to 10 pages (500 jobs) and writes new listings to the `jobs` table. Already-seen `adzuna_id` values are skipped, making repeated fetches safe.
2. **Extract** — Each description is scanned by a compiled regex pattern that matches 60+ tech skill phrases (longest match wins, case-insensitive). Each match is stored as a row in the `skills` table linked to the parent job.
3. **Aggregate** — The skills endpoints group by `skill_name` and count occurrences, with an optional date-bucket for the history chart.
4. **Analyze** — The résumé endpoint retrieves the current top-N skills from the database, then sends the résumé text alongside that ranked list to Claude Sonnet, which returns a structured JSON gap report.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- An [Adzuna API account](https://developer.adzuna.com/) (free tier: ~100 requests/day)
- An [Anthropic API key](https://console.anthropic.com/)

### 1 — Clone and configure

```bash
git clone https://github.com/your-username/job-market-analyzer.git
cd job-market-analyzer

cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite+aiosqlite:///./data/jobs.db
VITE_API_BASE_URL=http://localhost:8000
```

### 2 — Backend setup

```bash
cd backend

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

The API starts at **http://localhost:8000**. Interactive docs are at **http://localhost:8000/docs**.

> The SQLite database is created automatically at `backend/data/jobs.db` on first startup.

### 3 — Frontend setup

Open a second terminal:

```bash
cd frontend

npm install
npm run dev
```

The app opens at **http://localhost:5173**.

### 4 — First run

1. Type a keyword (e.g. `machine learning engineer`) into the search bar.
2. Select how many pages to fetch (start with **3 pages · 150 jobs**).
3. Click **Fetch Jobs** — the backend calls Adzuna, extracts skills, and populates the dashboard.
4. Paste your résumé into the **Resume Analyzer** section and click **Analyze Skills Gap**.

---

## API Reference

All endpoints are prefixed with `http://localhost:8000`.

### Jobs

#### `GET /jobs/fetch`
Pull new listings from Adzuna and extract skills. Idempotent — duplicate listings are skipped.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `keywords` | string | `software engineer` | Search terms |
| `country` | string | `us` | Two-letter country code (`us`, `gb`, `au`, …) |
| `pages` | integer | `1` | Pages to fetch (1–10, 50 results each) |

**Response**
```json
{
  "inserted": 143,
  "skipped": 7,
  "skills_extracted": 891,
  "pages_fetched": 3
}
```

---

#### `GET /jobs`
List stored job listings with pagination.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | `1` | Page number |
| `page_size` | integer | `20` | Results per page (max 100) |

**Response**
```json
{
  "total": 143,
  "page": 1,
  "page_size": 20,
  "jobs": [{ "id": 1, "title": "...", "company": "...", ... }]
}
```

---

### Skills

#### `GET /skills/trending`
Top N skills ranked by mention frequency across all stored job descriptions.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | `20` | Number of skills to return (max 100) |

**Response**
```json
{
  "skills": [
    { "skill_name": "Python", "count": 98 },
    { "skill_name": "SQL", "count": 76 }
  ],
  "total_jobs_analyzed": 143
}
```

---

#### `GET /skills/history`
Daily skill mention counts for the top-N skills — powers the line chart.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `top_n` | integer | `5` | Number of skills to track (max 20) |

**Response**
```json
{
  "history": [
    { "date": "2024-01-15", "skill_name": "Python", "count": 45 },
    { "date": "2024-01-16", "skill_name": "Python", "count": 53 }
  ]
}
```

---

### Resume

#### `POST /resume/analyze`
Analyze résumé text against the current top trending skills using Claude Sonnet.

**Request body**
```json
{
  "resume_text": "Experienced software engineer with 5 years of Python...",
  "top_n_skills": 30
}
```

**Response**
```json
{
  "match_score": 72,
  "summary": "Strong backend profile with solid Python and SQL skills...",
  "skills_you_have": ["Python", "SQL", "Docker", "AWS"],
  "skills_you_need": ["Kubernetes", "TypeScript", "React", "Terraform"],
  "recommendations": [
    "Complete a Kubernetes certification to complement your existing Docker expertise.",
    "..."
  ]
}
```

> **Note:** This endpoint requires at least one prior call to `GET /jobs/fetch` to populate the skills database.

---

## Project Structure

```
job-market-analyzer/
├── backend/
│   ├── main.py                  # FastAPI app + CORS + lifespan
│   ├── database.py              # SQLAlchemy async engine + settings
│   ├── requirements.txt
│   ├── models/
│   │   ├── job.py               # Job ORM model
│   │   └── skill.py             # Skill ORM model
│   ├── schemas/
│   │   ├── job.py               # Pydantic response schemas
│   │   └── skill.py
│   ├── routers/
│   │   ├── jobs.py              # GET /jobs/fetch, GET /jobs
│   │   ├── skills.py            # GET /skills/trending, GET /skills/history
│   │   └── resume.py            # POST /resume/analyze
│   └── services/
│       ├── adzuna.py            # Adzuna API client (httpx)
│       ├── nlp.py               # Regex skill extractor
│       └── anthropic_client.py  # Claude Sonnet gap analysis
└── frontend/
    ├── src/
    │   ├── App.jsx              # State management + layout
    │   ├── services/api.js      # Axios instance + API helpers
    │   ├── components/
    │   │   ├── Dashboard.jsx    # Stat cards + chart layout
    │   │   ├── SkillsBarChart.jsx
    │   │   ├── TrendLineChart.jsx
    │   │   ├── JobList.jsx
    │   │   └── ResumeAnalyzer.jsx
    │   └── styles/index.css     # Design system + skeleton animations
    └── package.json
```

---

## License

MIT © 2026 — see [LICENSE](LICENSE) for details.
