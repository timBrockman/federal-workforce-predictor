"""SQLAlchemy 2.0 models.

Originally spend budget domain; evolving to federal workforce / employee lifecycle + career readiness (EmployeeAssessment, CareerSignal)
lifecycle predictor (assessments + synthetic career signals).

Emphasizes auditability and ethics (consent records + decision logs) for
both domains. Old spend models retained during transition for reference.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    questionnaire_responses: Mapped[List["QuestionnaireResponse"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["SpendTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # New federal workforce relationships (added in same logical model expansion)
    employee_assessments: Mapped[List["EmployeeAssessment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    career_signals: Mapped[List["CareerSignal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    income_bracket: Mapped[str] = mapped_column(String(32))
    goals: Mapped[str] = mapped_column(Text)
    risk_tolerance: Mapped[str] = mapped_column(String(32))
    has_social_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_answers: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="questionnaire_responses")


class SpendTransaction(Base):
    __tablename__ = "spend_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(64), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="user")

    user: Mapped["User"] = relationship(back_populates="transactions")


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    purpose: Mapped[str] = mapped_column(String(128))
    granted: Mapped[bool] = mapped_column(Boolean)
    level: Mapped[int] = mapped_column(Integer, default=0)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EthicalDecisionLog(Base):
    __tablename__ = "ethical_decision_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    decision_type: Mapped[str] = mapped_column(String(64))
    allowed: Mapped[bool]
    reason: Mapped[str] = mapped_column(Text)
    data_sources: Mapped[list[str]] = mapped_column(JSON, default=list)
    classification: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


# =============================================================================
# New federal workforce / employee lifecycle domain models
# (added incrementally; synthetic data only for the reference implementation)
# =============================================================================

class EmployeeAssessment(Base):
    """Structured input analogous to the old questionnaire.

    Captures skills, performance signals, career intent, and explicit consent
    for use in career-trajectory and critical-role recommendations.
    """

    __tablename__ = "employee_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    skills_inventory: Mapped[str] = mapped_column(Text)  # e.g. "python,cloud,leadership"
    performance_level: Mapped[str] = mapped_column(String(32))  # high/medium/low + notes
    career_goals: Mapped[str] = mapped_column(Text)
    critical_role_interest: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_for_career_modeling: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_answers: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="employee_assessments")


class CareerSignal(Base):
    """Synthetic internal mobility / training / performance signals.

    Plays the role that "synthetic social" played in the spend domain.
    Only used when consent_for_career_modeling is granted.
    """

    __tablename__ = "career_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    signal_type: Mapped[str] = mapped_column(String(64))  # e.g. "mobility", "training", "cert"
    value: Mapped[str] = mapped_column(String(128))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str] = mapped_column(String(32), default="synthetic")

    user: Mapped["User"] = relationship(back_populates="career_signals")


