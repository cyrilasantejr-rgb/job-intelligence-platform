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

SENIOR_KEYWORDS = [
    "senior",
    "sr.",
    "sr",
    "staff",
    "principal",
    "distinguished",
    "lead",
    "director",
    "vp",
    "vice president",
    "head of",
    "chief",
    "executive",
    "president",
    "manager",
    "architect",
]


def _matches_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def infer_category(title: str, description: str | None = None) -> str | None:
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


def is_senior_role(title: str) -> bool:
    """True if the title contains a word-boundary match for a senior-level
    keyword (Senior, Staff, Director, Manager, etc.)."""
    text = title.lower()
    return any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in SENIOR_KEYWORDS)


def is_entry_level_friendly(title: str) -> bool:
    """
    True if the role looks appropriate for an internship/new-grad job
    seeker — either explicitly labeled as such, or simply not flagged as
    senior-level. This is deliberately permissive: a title with no
    seniority signal at all (e.g. plain "Software Engineer") is treated
    as beginner-friendly rather than excluded, since many companies don't
    label entry-level roles explicitly.
    """
    if infer_employment_type(title) is not None:
        return True
    return not is_senior_role(title)
