from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class RoleEnum(str, enum.Enum):
    owner = "Owner"
    editor = "Editor"
    viewer = "Viewer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    events = relationship("Event", back_populates="creator")
    permissions = relationship("Permission", back_populates="user")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="events")

    permissions = relationship("Permission", back_populates="event")
    histories = relationship("EventHistory", back_populates="event")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    role = Column(Enum(RoleEnum), default=RoleEnum.viewer)

    user = relationship("User", back_populates="permissions")
    event = relationship("Event", back_populates="permissions")

class EventHistory(Base):
    __tablename__ = "event_histories"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String)
    recurrence_pattern = Column(String)
    changed_by = Column(Integer, ForeignKey("users.id"))

    event = relationship("Event", back_populates="histories")
