from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    owner = "Owner"
    editor = "Editor"
    viewer = "Viewer"

# ---------- User Schemas ----------

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

# ---------- Auth Schemas ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginData(BaseModel):
    username: str
    password: str

# ---------- Event Schemas ----------

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    created_at: datetime
    creator_id: int
    class Config:
        orm_mode = True

# ---------- Permissions ----------

class ShareUser(BaseModel):
    user_id: int
    role: RoleEnum

class PermissionOut(BaseModel):
    user_id: int
    event_id: int
    role: RoleEnum
    class Config:
        orm_mode = True

# ---------- History and Versioning ----------

class EventHistoryOut(BaseModel):
    id: int
    event_id: int
    timestamp: datetime
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    recurrence_pattern: Optional[str]
    changed_by: int

    class Config:
        orm_mode = True

class DiffResponse(BaseModel):
    field: str
    old_value: Optional[str]
    new_value: Optional[str]
