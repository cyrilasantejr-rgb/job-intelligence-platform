"""
Job categorization.

Keyword-based heuristics, not ML — deliberately simple and explainable per
the project's "simpler professional implementation" principle. Each rule
is easy to read, test, and extend. If this proves too coarse later, it can
be swapped for an embeddings-based classifier without touching callers,
since the function signature stays the same.
"""

import re

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Data Engineering": ["data engineer", "data engineering", "etl", "data pipeline", "dbt"],
    "Machine Learning / AI": [
        "machine learning",
        "ml engineer",
        "ai engineer",
        "applied scientist",
        "research scientist",
    ],
    "Data Analytics": ["data analyst", "analytics", "business intelligence", "bi analyst"],
    "Cloud / Platform Engineering": [
        "platform engineer",
        "cloud engineer",
        "infrastructure engineer",
        "site reliability",
        "devops",
    ],
    "Software Engineering": [
        "software engineer",
        "software engineering",
        "swe",
        "backend engineer",
        "frontend engineer",
        "full stack",
    ],
}

EMPLOYMENT_TYPE_KEYWORDS: dict[str, list[str]] = {
    "Internship": ["intern", "internship", "co-op", "coop"],
    "New Grad": ["new grad", "new graduate", "university grad", "entry level", "early career"],
}


def _matches_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def infer_category(title: str, description: str | None = None) -> str | None:
    """
    Returns the first matching category, checked in CATEGORY_KEYWORDS order.

    Order matters: e.g. a title like "Machine Learning Data Engineer" would
    match both ML and Data Engineering keywords — we check ML first since
    the earlier categories in the dict are checked first. This is a
    reasonable default judgment call, not a hard rule; revisit if seed data
    shows it's picking the wrong category often.
    """
    text = f"{title} {description or ''}".lower()
    text = re.sub(r"\s+", " ", text)

    for category, keywords in CATEGORY_KEYWORDS.items():
        if _matches_any(text, keywords):
            return category
    return None


def infer_employment_type(title: str) -> str | None:
    text = title.lower()
    for employment_type, keywords in EMPLOYMENT_TYPE_KEYWORDS.items():
        if _matches_any(text, keywords):
            return employment_type
    return None
