from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from . import models, schemas, database, auth

router = APIRouter(prefix="/api/events", tags=["Events"])

get_db = database.SessionLocal

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- Create Event ----------------
@router.post("/", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_event = models.Event(
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        is_recurring=event.is_recurring,
        recurrence_pattern=event.recurrence_pattern,
        creator_id=current_user.id,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Assign the creator as Owner
    permission = models.Permission(user_id=current_user.id, event_id=new_event.id, role="Owner")
    db.add(permission)
    db.commit()

    return new_event

# ---------------- Get All Events (paginated) ----------------
@router.get("/", response_model=List[schemas.EventOut])
def get_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permissions = db.query(models.Permission).filter(models.Permission.user_id == current_user.id).all()
    event_ids = [p.event_id for p in permissions]
    events = db.query(models.Event).filter(models.Event.id.in_(event_ids)).offset(skip).limit(limit).all()
    return events

# ---------------- Get Single Event ----------------
@router.get("/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    event = db.query(models.Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# ---------------- Update Event ----------------
@router.put("/{event_id}", response_model=schemas.EventOut)
def update_event(event_id: int, event_data: schemas.EventUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission or permission.role not in ("Owner", "Editor"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    event = db.query(models.Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Save current version to history
    history = models.EventHistory(
        event_id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        recurrence_pattern=event.recurrence_pattern,
        changed_by=current_user.id,
    )
    db.add(history)

    for attr, value in event_data.dict().items():
        setattr(event, attr, value)
    
    db.commit()
    db.refresh(event)
    return event

# ---------------- Delete Event ----------------
@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission or permission.role != "Owner":
        raise HTTPException(status_code=403, detail="Only owner can delete the event")

    event = db.query(models.Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return

# ---------------- Batch Create Events ----------------
@router.post("/batch", response_model=List[schemas.EventOut])
def batch_create(events: List[schemas.EventCreate], db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    event_list = []
    for event in events:
        new_event = models.Event(
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            is_recurring=event.is_recurring,
            recurrence_pattern=event.recurrence_pattern,
            creator_id=current_user.id,
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        event_list.append(new_event)

        permission = models.Permission(user_id=current_user.id, event_id=new_event.id, role="Owner")
        db.add(permission)
        db.commit()

    return event_list
