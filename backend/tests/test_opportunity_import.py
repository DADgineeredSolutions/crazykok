from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models
from backend.app.database import Base
from backend.app.opportunity_import import import_opportunities


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'import.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_import_opportunities_cleans_junk_and_links_series_and_venue(db_session):
    junk = models.Opportunity(
        name="Winter Market",
        location="Assen",
        event_date=date(2026, 12, 1),
        organizer="Test Organizer",
        category="Market",
        application_status="researching",
    )
    db_session.add(junk)
    db_session.commit()

    result = import_opportunities(
        db_session,
        [
            {
                "import_key": "OPP-NL-DR-EMMEN-WEEKMARKT-2026-07-17",
                "name": "Emmen centrum weekmarkt 2026-07-17",
                "series_name": "Emmen centrum weekmarkt",
                "event_date": "2026-07-17",
                "application_deadline": "",
                "organizer": "Gemeente Emmen",
                "category": "Market",
                "location": "Marktplein Emmen",
                "venue_external_id": "VEN-NL-DR-EMMEN-MARKTPLEIN",
                "venue_name": "Marktplein Emmen",
                "application_status": "researching",
                "source_url": "",
                "notes": "Verify before applying.",
                "expected_revenue": "",
                "expected_attendance": "",
                "profit_score": "55",
                "is_active": "true",
            }
        ],
        clean_regression_junk=True,
        seed_venues=True,
    )
    db_session.commit()

    assert result.junk_deleted == 1
    assert result.created == 1
    assert db_session.query(models.Opportunity).filter(models.Opportunity.name == "Winter Market").count() == 0
    opportunity = db_session.query(models.Opportunity).filter(
        models.Opportunity.name == "Emmen centrum weekmarkt 2026-07-17"
    ).one()
    assert opportunity.series.name == "Emmen centrum weekmarkt"
    assert opportunity.venue.venue_external_id == "VEN-NL-DR-EMMEN-MARKTPLEIN"
    assert opportunity.profit_score == 55


def test_import_opportunities_is_idempotent_by_name_date_and_venue(db_session):
    row = {
        "import_key": "OPP-NL-DR-ASSEN-RACE",
        "name": "Assen race 2026",
        "series_name": "Assen race",
        "event_date": "2026-08-02",
        "application_deadline": "",
        "organizer": "TT Circuit Assen",
        "category": "Race event",
        "location": "TT Circuit Assen",
        "venue_external_id": "VEN-NL-DR-TT-CIRCUIT",
        "venue_name": "TT Circuit Assen",
        "application_status": "researching",
        "source_url": "",
        "notes": "First pass.",
        "expected_revenue": "",
        "expected_attendance": "",
        "profit_score": "70",
        "is_active": "true",
    }
    first = import_opportunities(db_session, [row], seed_venues=True)
    second = import_opportunities(db_session, [{**row, "notes": "Updated."}], seed_venues=True)
    db_session.commit()

    assert first.created == 1
    assert second.updated == 1
    assert db_session.query(models.Opportunity).count() == 1
    assert db_session.query(models.Opportunity).one().notes == "Updated."


def test_import_opportunities_keeps_distinct_rows_with_shared_source_url(db_session):
    base = {
        "series_name": "TT race series",
        "event_date": "2026-08-02",
        "application_deadline": "",
        "organizer": "TT Circuit Assen",
        "category": "Race event",
        "location": "TT Circuit Assen",
        "venue_external_id": "VEN-NL-DR-TT-CIRCUIT",
        "venue_name": "TT Circuit Assen",
        "application_status": "researching",
        "source_url": "https://www.supercarchallenge.nl/",
        "notes": "",
        "expected_revenue": "",
        "expected_attendance": "",
        "profit_score": "",
        "is_active": "true",
    }

    result = import_opportunities(
        db_session,
        [
            {"import_key": "one", "name": "JACK'S Racing Days 2026", **base},
            {"import_key": "two", "name": "Supercar Madness Finale Races 2026", **base, "event_date": "2026-10-25"},
        ],
        seed_venues=True,
    )
    db_session.commit()

    assert result.created == 2
    assert db_session.query(models.Opportunity).count() == 2
