"""
Companies to pull job postings from via the Greenhouse Job Board API.

IMPORTANT: Greenhouse doesn't publish a directory of which companies use
it or what their board token is — there's no way to enumerate this
programmatically. Each token below is a guess based on the company's
likely board-token naming pattern (usually a lowercase, no-space version
of the company name), not something verified against a live API call —
this sandbox can't reach boards-api.greenhouse.io to confirm.

Run `python -m app.ingestion.run_ingestion` and check the logs: any token
that returns "not found (404) — skipping" either isn't on Greenhouse, uses
a different token, or has since switched ATS providers. Swap in working
tokens as you discover them — this list is meant to be edited.

To find a real token yourself: if a company's careers page links to
boards.greenhouse.io/<something>, that <something> is the board_token.
"""

BOARD_TOKENS = [
    "stripe",
    "robinhood",
    "doordash",
    "airbnb",
    "asana",
    "coinbase",
]
