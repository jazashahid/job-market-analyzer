import json
from typing import List, Optional
import anthropic
from database import settings

_client: Optional[anthropic.AsyncAnthropic] = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


async def analyze_resume_gap(resume_text: str, trending_skills: List[str]) -> dict:
    """Send résumé text + trending skills to Claude and return a structured gap report."""
    client = _get_client()
    skills_csv = ", ".join(trending_skills[:50])  # stay within prompt budget

    prompt = f"""You are a senior technical recruiter and career coach.

Analyze the résumé below against the current top trending skills in the job market.

TRENDING SKILLS (ranked by job market demand):
{skills_csv}

RÉSUMÉ TEXT:
{resume_text}

Return ONLY a JSON object — no markdown fences, no explanation — with exactly these keys:
{{
  "match_score": <integer 0-100, how well the résumé matches current market demand>,
  "summary": "<2-3 sentence plain-English overview>",
  "skills_you_have": ["skills from the trending list that appear in the résumé"],
  "skills_you_need": ["trending skills NOT found in the résumé, ordered by market importance"],
  "recommendations": ["3-5 concrete, actionable steps to close the skills gap"]
}}"""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences defensively in case the model adds them
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    return json.loads(raw)
