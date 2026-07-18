from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Iterable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models
from .opportunity_service import apply_opportunity_values


OPPORTUNITY_IMPORT_FIELDS = [
    "import_key",
    "name",
    "series_name",
    "event_date",
    "application_deadline",
    "organizer",
    "category",
    "location",
    "venue_external_id",
    "venue_name",
    "application_status",
    "source_url",
    "notes",
    "expected_revenue",
    "expected_attendance",
    "profit_score",
    "is_active",
]


@dataclass(frozen=True)
class OpportunityImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    junk_deleted: int = 0


def read_opportunity_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return read_opportunity_csv_text(handle.read())


def read_opportunity_csv_text(content: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(content.lstrip("\ufeff")))
    missing = sorted(set(OPPORTUNITY_IMPORT_FIELDS) - set(reader.fieldnames or []))
    if missing:
        raise ValueError(f"Missing required opportunity import columns: {', '.join(missing)}")
    return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def cleanup_regression_junk(db: Session) -> int:
    explicit_junk = (
        db.query(models.Opportunity)
        .filter(
            models.Opportunity.name == "Winter Market",
            models.Opportunity.location == "Assen",
            models.Opportunity.organizer == "Test Organizer",
            models.Opportunity.category == "Market",
            models.Opportunity.event_date == date(2026, 12, 1),
            or_(models.Opportunity.source_url.is_(None), models.Opportunity.source_url == ""),
        )
        .all()
    )

    valid_statuses = {"researching", "watchlist", "applied", "accepted", "declined", "waitlisted"}
    regression_artifacts = []
    for record in db.query(models.Opportunity).all():
        name = record.name or ""
        status = record.application_status or ""
        has_source = bool(record.source_url and record.source_url.startswith(("http://", "https://")))
        has_series = record.opportunity_series_id is not None
        has_engagements = bool(record.engagements)
        has_printable_name = name.isprintable()
        has_ascii_name = name.isascii()
        impossible_date = record.event_date is not None and record.event_date.year < 2020
        placeholder_name = name.strip().lower() in {"0", "false", "x"}
        if has_source or has_series or has_engagements:
            continue
        if status not in valid_statuses or not has_printable_name or not has_ascii_name or impossible_date or placeholder_name:
            regression_artifacts.append(record)

    junk_by_id = {record.id: record for record in [*explicit_junk, *regression_artifacts]}
    for record in junk_by_id.values():
        db.delete(record)
    return len(junk_by_id)


def ensure_local_seed_venues(db: Session) -> None:
    seeds = [
        {
            "venue_external_id": "VEN-NL-DR-EMMEN-MARKTPLEIN",
            "venue_name": "Marktplein Emmen",
            "venue_slug": "marktplein-emmen",
            "venue_category_primary": "town_square",
            "town": "Emmen",
            "municipality": "Emmen",
            "province": "Drenthe",
            "country": "Netherlands",
            "geocode_precision": "town_or_area",
            "geocode_source": "manual",
            "research_status": "identified",
            "confidence_rating": "D",
            "data_owner_notes": "Local opportunity seed venue; verify exact pitch area before relying on it.",
            "active": True,
        },
        {
            "venue_external_id": "VEN-NL-DR-TT-CIRCUIT",
            "venue_name": "TT Circuit Assen",
            "venue_slug": "tt-circuit-assen",
            "venue_category_primary": "sports_complex",
            "street_address": "De Haar 9",
            "postcode": "9405 TE",
            "town": "Assen",
            "municipality": "Assen",
            "province": "Drenthe",
            "country": "Netherlands",
            "latitude": 52.9621,
            "longitude": 6.5242,
            "geocode_precision": "venue_centroid",
            "geocode_source": "manual",
            "website_url": "https://www.ttcircuit.com/",
            "research_status": "identified",
            "confidence_rating": "C",
            "data_owner_notes": "Local opportunity seed venue; verify vendor access and pitch details per race.",
            "active": True,
        },
    ]
    for values in seeds:
        venue = (
            db.query(models.Venue)
            .filter(models.Venue.venue_external_id == values["venue_external_id"])
            .first()
        )
        if venue is None:
            venue = models.Venue()
            db.add(venue)
        for field, value in values.items():
            setattr(venue, field, value)


def _parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def _parse_int(value: str) -> int | None:
    return int(value) if value else None


def _parse_float(value: str) -> float | None:
    return float(value) if value else None


def _parse_bool(value: str) -> bool:
    return value.lower() not in {"false", "0", "no", "n"}


def _find_venue(db: Session, row: dict[str, str]) -> models.Venue | None:
    if row.get("venue_external_id"):
        venue = (
            db.query(models.Venue)
            .filter(models.Venue.venue_external_id == row["venue_external_id"])
            .first()
        )
        if venue is not None:
            return venue
    if row.get("venue_name"):
        return db.query(models.Venue).filter(models.Venue.venue_name == row["venue_name"]).first()
    return None


def _find_existing(db: Session, row: dict[str, str], event_date: date | None, venue_id: int | None) -> models.Opportunity | None:
    if row["source_url"]:
        existing = (
            db.query(models.Opportunity)
            .filter(
                models.Opportunity.source_url == row["source_url"],
                models.Opportunity.name == row["name"],
            )
            .first()
        )
        if existing is not None:
            return existing
    query = db.query(models.Opportunity).filter(
        models.Opportunity.name == row["name"],
        models.Opportunity.event_date == event_date,
    )
    if venue_id is not None:
        query = query.filter(models.Opportunity.venue_id == venue_id)
    else:
        query = query.filter(models.Opportunity.location == (row["location"] or None))
    return query.first()


def import_opportunities(
    db: Session,
    rows: Iterable[dict[str, str]],
    *,
    clean_regression_junk: bool = False,
    seed_venues: bool = False,
) -> OpportunityImportResult:
    junk_deleted = cleanup_regression_junk(db) if clean_regression_junk else 0
    if seed_venues:
        ensure_local_seed_venues(db)
        db.flush()

    created = 0
    updated = 0
    skipped = 0
    for row in rows:
        if not row.get("name"):
            skipped += 1
            continue
        event_date = _parse_date(row["event_date"])
        venue = _find_venue(db, row)
        existing = _find_existing(db, row, event_date, venue.id if venue else None)
        opportunity = existing or models.Opportunity()
        values = {
            "name": row["name"],
            "description": None,
            "location": row["location"] or (venue.venue_name if venue else None),
            "event_date": event_date,
            "application_deadline": _parse_date(row["application_deadline"]),
            "organizer": row["organizer"] or None,
            "category": row["category"] or None,
            "application_status": row["application_status"] or "researching",
            "source_url": row["source_url"] or None,
            "notes": row["notes"] or None,
            "expected_revenue": _parse_int(row["expected_revenue"]),
            "expected_attendance": _parse_int(row["expected_attendance"]),
            "profit_score": _parse_float(row["profit_score"]),
            "is_active": _parse_bool(row["is_active"]),
            "venue_id": venue.id if venue else None,
            "series_name": row["series_name"] or None,
        }
        apply_opportunity_values(db, opportunity, values)
        if existing is None:
            db.add(opportunity)
            created += 1
        else:
            updated += 1
        db.flush()

    return OpportunityImportResult(
        created=created,
        updated=updated,
        skipped=skipped,
        junk_deleted=junk_deleted,
    )
