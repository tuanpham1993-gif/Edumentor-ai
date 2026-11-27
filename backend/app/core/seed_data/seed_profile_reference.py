"""Seed certifications and technical_domains (form options for learning_path2).

Runs at startup (core/database.init_db). Each table is filled only when empty, so admin
edits are never overwritten. Source files: datajson/certifications.json, datajson/technical_domains.json.
"""
import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.profile_reference import Certification, TechnicalDomain

DATAJSON = Path(__file__).resolve().parents[4] / "datajson"


def seed_profile_reference(db: Session, datajson: Path = DATAJSON) -> dict[str, int]:
    added = {"certifications": 0, "technical_domains": 0}
    try:
        if db.execute(select(func.count(Certification.cert_id))).scalar_one() == 0:
            rows = json.loads((datajson / "certifications.json").read_text(encoding="utf-8"))
            db.add_all(Certification(name=r["name"], issuer=r.get("issuer"), aliases=r.get("aliases", []))
                       for r in rows)
            added["certifications"] = len(rows)
        if db.execute(select(func.count(TechnicalDomain.domain_id))).scalar_one() == 0:
            rows = json.loads((datajson / "technical_domains.json").read_text(encoding="utf-8"))
            db.add_all(TechnicalDomain(name=r["name"]) for r in rows)
            added["technical_domains"] = len(rows)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return added
