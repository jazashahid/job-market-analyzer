"""
Pytest test suite for the Job Market Analyzer API.

All external calls (Adzuna and Anthropic) are mocked so tests run without
live credentials or network access.
"""

import pytest
from unittest.mock import AsyncMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LONG_RESUME = (
    "Experienced Python developer with five years of professional experience. "
    "Proficient in Docker, AWS, and PostgreSQL. "
    "Skilled in REST API design, Git workflows, and Agile practices. "
) * 3  # well above the 50-char minimum

MOCK_ADZUNA_RESULTS = [
    {
        "adzuna_id": "adzuna-001",
        "title": "Senior Python Developer",
        "company": "Acme Corp",
        "location": "New York, NY",
        "description": (
            "We need a Python developer experienced with Docker, AWS, "
            "PostgreSQL, and REST API design. Kubernetes a plus."
        ),
        "salary_min": 90_000.0,
        "salary_max": 130_000.0,
        "category": "IT Jobs",
        "url": "https://example.com/jobs/adzuna-001",
    }
]

MOCK_ANTHROPIC_RESULT = {
    "match_score": 78,
    "summary": "Strong backend profile with good cloud coverage.",
    "skills_you_have": ["Python", "Docker", "AWS", "PostgreSQL"],
    "skills_you_need": ["Kubernetes", "GraphQL"],
    "recommendations": [
        "Obtain AWS Solutions Architect certification.",
        "Build a Kubernetes side-project.",
        "Add GraphQL to an existing REST service.",
    ],
}


async def _seed_job_with_skills(db_session, adzuna_id: str = "job-seed-1"):
    """Insert one Job + a handful of Skill rows for tests that need existing data."""
    from models.job import Job
    from models.skill import Skill

    job = Job(
        adzuna_id=adzuna_id,
        title="Python Developer",
        description="Python, Docker, AWS, PostgreSQL needed.",
        url=f"https://example.com/jobs/{adzuna_id}",
    )
    db_session.add(job)
    await db_session.flush()

    for name in ["Python", "Docker", "AWS", "PostgreSQL"]:
        db_session.add(Skill(job_id=job.id, skill_name=name))

    await db_session.commit()
    return job


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


async def test_health_returns_200(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /jobs
# ---------------------------------------------------------------------------


async def test_list_jobs_empty(client):
    response = await client.get("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["jobs"] == []
    assert data["page"] == 1
    assert data["page_size"] == 20


async def test_list_jobs_returns_paginated_results(client, db_session):
    from models.job import Job

    for i in range(7):
        db_session.add(
            Job(
                adzuna_id=f"job-{i}",
                title=f"Engineer {i}",
                description="Python developer needed.",
                url=f"https://example.com/jobs/{i}",
            )
        )
    await db_session.commit()

    response = await client.get("/jobs?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 7
    assert len(data["jobs"]) == 5
    assert data["page"] == 1
    assert data["page_size"] == 5

    # Second page
    response2 = await client.get("/jobs?page=2&page_size=5")
    data2 = response2.json()
    assert data2["total"] == 7
    assert len(data2["jobs"]) == 2


async def test_list_jobs_response_shape(client, db_session):
    from models.job import Job

    db_session.add(
        Job(
            adzuna_id="shape-job",
            title="DevOps Engineer",
            company="TechCo",
            location="San Francisco, CA",
            description="Docker and Kubernetes experience required.",
            salary_min=100_000.0,
            salary_max=150_000.0,
            category="IT Jobs",
            url="https://example.com/jobs/shape-job",
        )
    )
    await db_session.commit()

    response = await client.get("/jobs")
    job = response.json()["jobs"][0]
    for field in ("id", "adzuna_id", "title", "description", "url", "fetched_at"):
        assert field in job, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# GET /skills/trending
# ---------------------------------------------------------------------------


async def test_trending_skills_empty(client):
    response = await client.get("/skills/trending")
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == []
    assert data["total_jobs_analyzed"] == 0


async def test_trending_skills_returns_skills_with_counts(client, db_session):
    await _seed_job_with_skills(db_session)

    response = await client.get("/skills/trending?limit=10")
    assert response.status_code == 200
    data = response.json()

    assert len(data["skills"]) > 0
    assert data["total_jobs_analyzed"] == 1

    skill_names = [s["skill_name"] for s in data["skills"]]
    assert "Python" in skill_names

    # Every entry must have the right shape
    for entry in data["skills"]:
        assert "skill_name" in entry
        assert isinstance(entry["count"], int)
        assert entry["count"] >= 1


async def test_trending_skills_respects_limit(client, db_session):
    await _seed_job_with_skills(db_session)  # seeds 4 distinct skills

    response = await client.get("/skills/trending?limit=2")
    data = response.json()
    assert len(data["skills"]) <= 2


# ---------------------------------------------------------------------------
# GET /skills/history
# ---------------------------------------------------------------------------


async def test_skill_history_empty(client):
    response = await client.get("/skills/history")
    assert response.status_code == 200
    assert response.json() == {"history": []}


async def test_skill_history_returns_data(client, db_session):
    await _seed_job_with_skills(db_session)

    response = await client.get("/skills/history?top_n=4")
    assert response.status_code == 200
    data = response.json()

    assert "history" in data
    assert len(data["history"]) > 0

    for point in data["history"]:
        assert "date" in point
        assert "skill_name" in point
        assert isinstance(point["count"], int)


async def test_skill_history_only_includes_top_n(client, db_session):
    await _seed_job_with_skills(db_session)  # 4 distinct skills

    response = await client.get("/skills/history?top_n=2")
    data = response.json()

    returned_skills = {p["skill_name"] for p in data["history"]}
    assert len(returned_skills) <= 2


# ---------------------------------------------------------------------------
# POST /resume/analyze
# ---------------------------------------------------------------------------


async def test_resume_analyze_returns_expected_fields(client, db_session):
    await _seed_job_with_skills(db_session)

    with patch(
        "services.anthropic_client.analyze_resume_gap",
        new_callable=AsyncMock,
        return_value=MOCK_ANTHROPIC_RESULT,
    ):
        response = await client.post(
            "/resume/analyze",
            json={"resume_text": LONG_RESUME, "top_n_skills": 10},
        )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["match_score"], int)
    assert 0 <= data["match_score"] <= 100
    assert isinstance(data["summary"], str)
    assert isinstance(data["skills_you_have"], list)
    assert isinstance(data["skills_you_need"], list)
    assert isinstance(data["recommendations"], list)


async def test_resume_analyze_404_when_no_skills_in_db(client):
    """Endpoint must 404 if no job/skill data has been ingested yet."""
    response = await client.post(
        "/resume/analyze",
        json={"resume_text": LONG_RESUME, "top_n_skills": 10},
    )
    assert response.status_code == 404


async def test_resume_analyze_passes_skills_to_anthropic(client, db_session):
    """Verify the correct skill names are forwarded to the Anthropic client."""
    await _seed_job_with_skills(db_session)

    mock_fn = AsyncMock(return_value=MOCK_ANTHROPIC_RESULT)
    with patch("services.anthropic_client.analyze_resume_gap", mock_fn):
        response = await client.post(
            "/resume/analyze",
            json={"resume_text": LONG_RESUME, "top_n_skills": 10},
        )

    assert response.status_code == 200
    call_args = mock_fn.call_args
    resume_arg, skills_arg = call_args[0]
    assert "Python" in skills_arg


# ---------------------------------------------------------------------------
# POST /resume/analyze — rate limiting (5 req/min per IP)
# ---------------------------------------------------------------------------


async def test_resume_analyze_rate_limit(client, db_session):
    """The 6th request within a minute must receive HTTP 429."""
    await _seed_job_with_skills(db_session)

    payload = {"resume_text": LONG_RESUME, "top_n_skills": 10}

    with patch(
        "services.anthropic_client.analyze_resume_gap",
        new_callable=AsyncMock,
        return_value=MOCK_ANTHROPIC_RESULT,
    ):
        for i in range(5):
            r = await client.post("/resume/analyze", json=payload)
            assert r.status_code == 200, f"Request {i + 1} unexpectedly failed: {r.text}"

        # 6th request must be blocked
        r = await client.post("/resume/analyze", json=payload)

    assert r.status_code == 429
    body = r.json()
    assert "error" in body
    assert "rate" in body["error"].lower() or "limit" in body["error"].lower()


# ---------------------------------------------------------------------------
# GET /jobs/fetch
# ---------------------------------------------------------------------------


async def test_fetch_jobs_returns_counts(client):
    with patch(
        "services.adzuna.fetch_jobs",
        new_callable=AsyncMock,
        return_value=MOCK_ADZUNA_RESULTS,
    ):
        response = await client.get("/jobs/fetch")

    assert response.status_code == 200
    data = response.json()
    assert data["inserted"] == 1
    assert data["skipped"] == 0
    assert data["skills_extracted"] > 0
    assert data["pages_fetched"] == 1


async def test_fetch_jobs_skips_duplicates(client):
    """Fetching the same job twice must insert once and skip once."""
    with patch(
        "services.adzuna.fetch_jobs",
        new_callable=AsyncMock,
        return_value=MOCK_ADZUNA_RESULTS,
    ):
        await client.get("/jobs/fetch")
        response = await client.get("/jobs/fetch")

    data = response.json()
    assert data["inserted"] == 0
    assert data["skipped"] == 1


async def test_fetch_jobs_extracts_skills_into_db(client, db_session):
    """Skills extracted during /jobs/fetch must persist in the DB."""
    from models.skill import Skill
    from sqlalchemy import select

    with patch(
        "services.adzuna.fetch_jobs",
        new_callable=AsyncMock,
        return_value=MOCK_ADZUNA_RESULTS,
    ):
        await client.get("/jobs/fetch")

    result = await db_session.execute(select(Skill))
    skills = result.scalars().all()
    assert len(skills) > 0
    assert any(s.skill_name == "Python" for s in skills)


async def test_fetch_jobs_502_on_adzuna_error(client):
    """An Adzuna API failure on the first page must surface as HTTP 502."""
    with patch(
        "services.adzuna.fetch_jobs",
        new_callable=AsyncMock,
        side_effect=Exception("connection refused"),
    ):
        response = await client.get("/jobs/fetch")

    assert response.status_code == 502
    assert "Adzuna" in response.json()["detail"]
