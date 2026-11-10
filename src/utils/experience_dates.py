"""Derive career span from loosely formatted resume dates (best-effort)."""
from __future__ import annotations

import re
from calendar import monthrange
from datetime import date
from typing import List, Optional, Tuple

_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

_SEASONS = {
    "spring": 3,
    "summer": 6,
    "fall": 9,
    "autumn": 9,
    "winter": 12,
}

_PRESENT = frozenset(
    {"present", "current", "currently", "now", "ongoing", "today", "date", "till-date"}
)

_END_CONNECTOR = re.compile(r"^(?:to|till|until|up\s*to)\s+")


def _is_present(s: Optional[str]) -> bool:
    if not s:
        return False
    t = re.sub(r"\s+", " ", str(s).strip().lower()).strip(" .")
    t = _END_CONNECTOR.sub("", t)
    return t in _PRESENT or t.startswith("present") or t.startswith("current")


_BARE_YEAR_START_MONTH = 7
_BARE_YEAR_END_MONTH = 6


def _is_bare_year(tok: str) -> bool:
    return re.match(r"^\d{4}$", tok.strip()) is not None


def _month_year_from_token(tok: str) -> Optional[Tuple[int, int]]:
    t = tok.strip().lower()
    if not t:
        return None
    m = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", t)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return y, mo
        return None

    m = re.match(r"^(\d{4})[-/](\d{1,2})$", t)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return y, mo
        return None

    m = re.match(r"^(\d{1,2})[-/](\d{4})$", t)
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return y, mo
        return None

    m = re.match(r"^([a-z]+)[,.]?\s+(\d{4})$", t)
    if m:
        prefix = m.group(1)
        y = int(m.group(2))
        mo = _MONTHS.get(prefix) or _MONTHS.get(prefix[:3]) or _SEASONS.get(prefix)
        if mo:
            return y, mo

    m = re.match(r"^(\d{4})$", t)
    if m:
        return int(m.group(1)), 1
    return None


def _split_range(s: str) -> Optional[Tuple[str, str]]:
    """Split "Jan 2020 - Present" into its two halves.

    A bare dash split is not enough: ISO dates carry their own dashes
    ("2024-01 - 2024-12"), so separators surrounded by whitespace — and the word
    "to" — are tried first, and a naive split is only accepted when both halves
    actually look like dates.
    """
    for pattern in (
        r"\s+[-]\s+",
        r"\s+(?:to|till|until|up\s*to)\s+",
        r"\s*[-]\s*",
    ):
        parts = re.split(pattern, s, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) != 2:
            continue
        start_tok, end_tok = parts[0].strip(), parts[1].strip()
        if not start_tok or not end_tok:
            continue
        if _month_year_from_token(start_tok) and (
            _is_present(end_tok) or _month_year_from_token(end_tok)
        ):
            return start_tok, end_tok
    return None


def _range_bounds(
    raw: Optional[str],
    *,
    assume_end_month_last: bool = True,
    today: Optional[date] = None,
) -> Optional[Tuple[date, date]]:
    """Return (start_date, end_date inclusive-friendly) from one job's date span."""
    if not raw:
        return None
    today = today or date.today()
    s = raw.replace("–", "-").replace("—", "-").strip()

    parts = _split_range(s)
    if parts is None:
        return None

    start_tok, end_tok = parts

    sm = _month_year_from_token(start_tok)
    if sm is None:
        return None
    sy, smo = sm
    if _is_bare_year(start_tok):
        smo = _BARE_YEAR_START_MONTH
    start_d = date(sy, smo, 1)

    if _is_present(end_tok):
        end_d = today
    else:
        em = _month_year_from_token(end_tok)
        if em is None:
            return None
        ey, emo = em
        if _is_bare_year(end_tok):
            emo = _BARE_YEAR_END_MONTH
        last_day = monthrange(ey, emo)[1] if assume_end_month_last else 1
        end_d = date(ey, emo, last_day)
        end_d = min(end_d, today)

    if end_d < start_d:
        start_d, end_d = end_d, start_d
    return start_d, end_d


def _merge_ranges(ranges: List[Tuple[date, date]]) -> List[Tuple[date, date]]:
    if not ranges:
        return []
    sr = sorted(ranges, key=lambda x: (x[0], x[1]))
    merged: List[Tuple[date, date]] = [sr[0]]
    for a, b in sr[1:]:
        pm0, pm1 = merged[-1]
        if a <= pm1:
            merged[-1] = (pm0, max(pm1, b))
        else:
            merged.append((a, b))
    return merged


def _entry_bounds(exp, *, today: date) -> Optional[Tuple[date, date]]:
    """Date span of a single experience entry, or None when it can't be parsed."""
    start_raw = (getattr(exp, "start_date", None) or "").strip()
    end_raw = (getattr(exp, "end_date", None) or "").strip()
    if not start_raw:
        return None

    if _month_year_from_token(start_raw) is None:
        return _range_bounds(start_raw, today=today)

    if end_raw:
        return _range_bounds(f"{start_raw} - {end_raw}", today=today)

    sy, smo = _month_year_from_token(start_raw)
    if _is_bare_year(start_raw):
        smo = _BARE_YEAR_START_MONTH
    start_d = date(sy, smo, 1)
    return (start_d, today) if start_d <= today else None


def parse_experience_ranges(
    experience: list,
    *,
    today: Optional[date] = None,
) -> Tuple[List[Tuple[date, date]], list]:
    """Split entries into (parsed date ranges, entries whose dates could not be parsed)."""
    today = today or date.today()
    ranges: List[Tuple[date, date]] = []
    unparsed: list = []
    for exp in experience:
        b = _entry_bounds(exp, today=today)
        if b:
            ranges.append(b)
        else:
            unparsed.append(exp)
    return ranges, unparsed


def years_from_ranges(ranges: List[Tuple[date, date]]) -> Optional[float]:
    """Union of date ranges converted to fractional years (overlaps counted once)."""
    merged = _merge_ranges(ranges)
    if not merged:
        return None
    days = sum((b - a).days + 1 for a, b in merged)
    return round(days / 365.25, 2)


def total_calendar_years_from_experience_entries(
    experience: list,
    *,
    today: Optional[date] = None,
) -> Optional[float]:
    """
    Union of job date ranges converted to fractional years.

    Entries whose dates can't be parsed are skipped; use parse_experience_ranges
    when the caller needs to know which ones were dropped.
    """
    ranges, _ = parse_experience_ranges(experience, today=today)
    return years_from_ranges(ranges)

