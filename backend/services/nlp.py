import re
from typing import Dict, List

# Canonical skill names.  Add or remove entries here to tune extraction.
TECH_SKILLS: List[str] = [
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang",
    "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl",
    # Frontend
    "React", "Vue", "Angular", "Next.js", "Nuxt.js", "Svelte",
    "HTML", "CSS", "SASS", "Tailwind", "Webpack", "Vite", "Redux",
    # Backend / frameworks
    "Node.js", "Express", "FastAPI", "Django", "Flask", "Spring", "Rails",
    "ASP.NET", "Laravel",
    # Databases
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "Snowflake", "BigQuery",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
    "CI/CD", "Jenkins", "GitHub Actions", "CircleCI", "Linux", "Bash", "Unix",
    # Data / ML
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "scikit-learn", "pandas", "NumPy",
    "Apache Spark", "Hadoop", "Airflow", "dbt", "Kafka", "RabbitMQ",
    "Tableau", "Power BI", "Looker",
    # APIs / architecture
    "REST API", "GraphQL", "gRPC", "microservices",
    # General
    "Git", "Agile", "Scrum", "DevOps", "SQL", "NoSQL",
    # AI tooling
    "Hugging Face", "LangChain", "OpenAI", "NLTK",
]

_SKILL_LOOKUP: Dict[str, str] = {s.lower(): s for s in TECH_SKILLS}

# Build one compiled pattern.  Longer phrases come first in the alternation so
# "Machine Learning" is preferred over a hypothetical bare "Machine" match.
# Boundaries: not preceded/followed by an alphanumeric character, which handles
# skills that contain non-word chars (C++, Next.js, ASP.NET, scikit-learn …).
_PATTERN: re.Pattern = re.compile(
    r"(?<![a-zA-Z0-9])(?:"
    + "|".join(re.escape(s) for s in sorted(TECH_SKILLS, key=len, reverse=True))
    + r")(?![a-zA-Z0-9])",
    re.IGNORECASE,
)


def extract_skills(text: str) -> List[str]:
    """Return deduplicated canonical skill names found in *text*."""
    seen: set = set()
    skills: List[str] = []
    for match in _PATTERN.finditer(text):
        lower = match.group().lower()
        if lower not in seen:
            seen.add(lower)
            skills.append(_SKILL_LOOKUP.get(lower, match.group()))
    return skills
