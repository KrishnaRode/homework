# =============================================================================
#  File:        backend/app/syllabus/scraper.py
#  Description: Optional syllabus scraper extension point (not required at runtime).
#  Developer:   Krishna Rode
#  Version:     1
# =============================================================================
"""Scraper-ready architecture. PrepWell does NOT depend on live scraping to run.

This module is a clean extension point: implement `scrape_to_syllabus` against a
public syllabus page later, then `service.save_syllabus()` the normalized result.
"""
from __future__ import annotations

from typing import Any


def scrape_to_syllabus(url: str, klass: str, subject: str) -> dict[str, Any]:
    """Stub. Returns the normalized syllabus skeleton without any network call.

    Replace the body with real parsing (e.g. httpx + selectolax) when wiring a
    specific source. Keep the output in the normalized shape below.
    """
    return {
        "class": klass,
        "subject": subject,
        "source": url,
        "chapters": [],
        "_note": "Scraping not implemented; this is the scraper-ready skeleton.",
    }
