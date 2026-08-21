"""
Client for the Greenhouse public Job Board API.

Docs: https://developers.greenhouse.io/job-board.html
No authentication required for read access. Each company that uses
Greenhouse has a "board token" — e.g. boards.greenhouse.io/stripe has
board_token "stripe".
"""

import requests

from app.core.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"
TIMEOUT_SECONDS = 15


class GreenhouseFetchError(Exception):
    """Raised when a board can't be fetched — bad token, network issue, etc."""


def fetch_jobs_for_board(board_token: str) -> list[dict]:
    """
    Fetches all published jobs for a given Greenhouse board token.

    Returns an empty list (rather than raising) if the board doesn't exist
    or has zero postings — a 404 here just means "this company isn't using
    Greenhouse (or not at this token)," which is an expected outcome when
    iterating over a list of guessed/candidate tokens, not a hard failure.
    """
    url = f"{BASE_URL}/{board_token}/jobs"
    params = {"content": "true"}

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as e:
        raise GreenhouseFetchError(f"Network error fetching board '{board_token}': {e}") from e

    if response.status_code == 404:
        logger.warning("Board '%s' not found (404) — skipping.", board_token)
        return []

    if not response.ok:
        raise GreenhouseFetchError(
            f"Greenhouse API returned {response.status_code} for board '{board_token}': "
            f"{response.text[:200]}"
        )

    data = response.json()
    jobs = data.get("jobs", [])
    logger.info("Fetched %d job(s) from board '%s'.", len(jobs), board_token)
    return jobs
