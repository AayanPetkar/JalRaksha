import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship as sqlalchemy_relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="mr", nullable=False)
    fcm_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    locations: Mapped[List["Location"]] = sqlalchemy_relationship("Location", back_populates="user", cascade="all, delete-orphan")
    emergency_contacts: Mapped[List["EmergencyContact"]] = sqlalchemy_relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    citizen_reports: Mapped[List["CitizenReport"]] = sqlalchemy_relationship("CitizenReport", back_populates="user", cascade="all, delete-orphan")


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="DISASTER_OFFICIAL", nullable=False)
    jurisdiction_district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class EmergencyContact(Base, TimestampMixin):
    __tablename__ = "emergency_contacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = sqlalchemy_relationship("User", back_populates="emergency_contacts")
    preferences: Mapped[Optional["EmergencyCirclePreference"]] = sqlalchemy_relationship("EmergencyCirclePreference", back_populates="contact", uselist=False, cascade="all, delete-orphan")


class EmergencyCirclePreference(Base, TimestampMixin):
    __tablename__ = "emergency_circle_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("emergency_contacts.id", ondelete="CASCADE"), unique=True, nullable=False)
    notify_on_prepare: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notify_on_critical: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_on_distress: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    contact: Mapped["EmergencyContact"] = sqlalchemy_relationship("EmergencyContact", back_populates="preferences")

