"""
Skills taxonomy and extraction.

Same design philosophy as app.services.categorization: keyword matching,
not ML — simple, explainable, and easy to extend. This is deliberately the
single source of truth for "what counts as a skill" so that resumes and
job descriptions are compared using the exact same vocabulary; if a skill
isn't in this list, it can't be matched on either side.

Canonical casing is what gets stored/displayed (e.g. "PostgreSQL", not
"postgresql"); matching itself is case-insensitive.
"""

import re

SKILLS: list[str] = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
    "SQL", "R", "Scala", "Kotlin", "Swift", "PHP", "Ruby",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
    "Spring", "Express", "GraphQL", "REST", "Next.js",
    "Pandas", "NumPy", "Spark", "Apache Spark", "Airflow", "dbt", "Kafka",
    "ETL", "Hadoop", "Data Warehousing", "Snowflake", "BigQuery",
    "Redshift", "Databricks",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "Scikit-learn", "NLP", "Computer Vision", "LLM", "Generative AI",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Cassandra",
    "DynamoDB", "Elasticsearch",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux",
    "CI/CD", "Jenkins", "GitHub Actions", "Microservices",
    "Git", "Agile", "Scrum", "Tableau", "Power BI", "Excel", "JIRA",
    "HTML", "CSS",
]

_SORTED_SKILLS = sorted(SKILLS, key=len, reverse=True)


def extract_skills(text: str | None) -> list[str]:
    """
    Returns the canonical-cased list of skills found in `text`, deduplicated
    and sorted alphabetically. Matching is case-insensitive and uses word
    boundaries (so "Go" doesn't match inside "Google", "R" doesn't match
    inside "React", etc.).
    """
    if not text:
        return []

    found: set[str] = set()
    for skill in _SORTED_SKILLS:
        pattern = rf"(?<![\w+#]){re.escape(skill)}(?![\w+#])"
        if re.search(pattern, text, re.IGNORECASE):
            found.add(skill)

    return sorted(found)
