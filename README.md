# Job Market Trend Analyzer

> Pull live job listings, extract trending skills, and see how your resume stacks up against the market.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com) [![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev) [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org) [![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org) [![Recharts](https://img.shields.io/badge/Recharts-2.x-22B5BF?style=flat-square&logo=javascript&logoColor=white)](https://recharts.org) [![Claude](https://img.shields.io/badge/Claude-Sonnet-D97706?style=flat-square)](https://anthropic.com) [![License: MIT](https://img.shields.io/badge/License-MIT-6B9E6B?style=flat-square)](LICENSE)

---

![Dashboard Screenshot](screenshot-dashboard.png)
![Resume Analyzer Screenshot](screenshot-resume.png)

---

## What it does

Fetches job listings from the [Adzuna API](https://developer.adzuna.com/), runs a compiled regex matcher over every description to extract 60+ tech skills, and stores everything in SQLite. The dashboard shows which skills appear most often and how that's changed over time. The resume analyzer sends your resume text + the current trending skills to Claude Sonnet, which comes back with a match score, a skills gap breakdown, and a short list of things to work on.

**Stack:** FastAPI + SQLAlchemy 2.0 (async) + SQLite on the backend, React 18 + Vite + Recharts on the frontend. Skill extraction is pure Python `re` — no compiled NLP deps, works anywhere.

## Setup

**Prerequisites:** Python 3.8+, Node.js 18+, an [Adzuna API account](https://developer.adzuna.com/) (free tier: ~100 req/day), and an [Anthropic API key](https://console.anthropic.com/).

### Backend

```bash
git clone https://github.com/your-username/job-market-analyzer.git
cd job-market-analyzer

cp .env.example .env   # fill in your keys — see Environment variables below

cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API at `http://localhost:8000` · Docs at `http://localhost:8000/docs` · DB auto-created at `backend/data/jobs.db`

### Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

### First run

1. Enter a keyword in the toolbar (e.g. `machine learning engineer`).
2. Pick a page count (3 pages = 150 jobs is a good start) and click **Fetch Jobs**.
3. Paste your resume into the analyzer section and click **Analyze Skills Gap**.

## Environment variables

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite+aiosqlite:///./data/jobs.db
VITE_API_BASE_URL=http://localhost:8000
```

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/jobs/fetch` | Fetch from Adzuna and extract skills. Params: `keywords`, `country` (default `us`), `pages` (1–10) |
| `GET` | `/jobs` | Paginated job list. Params: `page`, `page_size` (max 100) |
| `GET` | `/skills/trending` | Top N skills by mention count. Param: `limit` (default 20) |
| `GET` | `/skills/history` | Daily counts for top-N skills (powers the line chart). Param: `top_n` |
| `POST` | `/resume/analyze` | Resume gap analysis. Body: `{ "resume_text": "...", "top_n_skills": 30 }` |

`/jobs/fetch` is idempotent — duplicate listings are skipped on re-fetch. `/resume/analyze` requires at least one prior fetch to populate the skills database.

## License

MIT © 2026
