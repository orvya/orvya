from __future__ import annotations

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class LimitKind(str, enum.Enum):
    USERS = "users"
    MONITORED_CASES = "monitored_cases"
    STORAGE = "storage"


class FeatureKey(str, enum.Enum):
    CORE = "core"
    PUBLICATIONS = "publications"
    DOCUMENTS = "documents"
    TEMPLATES = "templates"
    FINANCE = "finance"
    REPORTS = "reports"


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    features: Mapped[list[PlanFeature]] = relationship(back_populates="plan", cascade="all, delete-orphan")
    limits: Mapped[list[PlanLimit]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class PlanFeature(Base):
    __tablename__ = "plan_features"
    __table_args__ = (UniqueConstraint("plan_id", "feature_key"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"))
    feature_key: Mapped[FeatureKey] = mapped_column(Enum(FeatureKey, name="feature_key"))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    plan: Mapped[Plan] = relationship(back_populates="features")


class PlanLimit(Base):
    __tablename__ = "plan_limits"
    __table_args__ = (UniqueConstraint("plan_id", "limit_kind"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"))
    limit_kind: Mapped[LimitKind] = mapped_column(Enum(LimitKind, name="limit_kind"))
    value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pending: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[Plan] = relationship(back_populates="limits")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    tax_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    institutional_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="America/Sao_Paulo")
    logo_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus, name="account_status"))
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("plans.id"))
    trial_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status"))
    is_system_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    permissions: Mapped[dict[str, bool]] = mapped_column(JSONB, default=dict)
    photo_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
