"""Reference lists for the "Make learning path" form (learning_path2).

certifications     : certifications a learner can say they hold (seed: datajson/certifications.json)
technical_domains  : broad specializations, e.g. "Backend Development" (seed: datajson/technical_domains.json)

The frontend loads both for its pickers; the G1 normalizer links the names the LLM extracts
to these rows (exact or alias, case-insensitive). Skills come from the existing `skills` table.
"""
from sqlalchemy import JSON, Boolean, Column, Integer, String, text

from app.core.database import Base


class Certification(Base):
    __tablename__ = "certifications"

    cert_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)
    issuer = Column(String(100), nullable=True)
    aliases = Column(JSON, nullable=False, default=list)   # other spellings, e.g. ["CKA"]
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))


class TechnicalDomain(Base):
    __tablename__ = "technical_domains"

    domain_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
