from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.database import SessionLocal
from backend.app.opportunity_import import import_opportunities, read_opportunity_csv


DEFAULT_CSV = ROOT / "templates" / "opportunities_local_seed.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Import local opportunity and series seed data.")
    parser.add_argument("csv_file", nargs="?", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--clean-regression-junk", action="store_true")
    parser.add_argument("--seed-venues", action="store_true")
    args = parser.parse_args()

    rows = read_opportunity_csv(args.csv_file)
    db = SessionLocal()
    try:
        result = import_opportunities(
            db,
            rows,
            clean_regression_junk=args.clean_regression_junk,
            seed_venues=args.seed_venues,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(
        "Opportunity import complete: "
        f"{result.created} created, {result.updated} updated, "
        f"{result.skipped} skipped, {result.junk_deleted} regression junk deleted."
    )


if __name__ == "__main__":
    main()
