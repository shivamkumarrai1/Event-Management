from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database, auth

router = APIRouter(prefix="/api/events", tags=["Version History & Diff"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Get Event History ----------
@router.get("/{event_id}/changelog", response_model=List[schemas.EventHistoryOut])
def get_changelog(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission:
        raise HTTPException(status_code=403, detail="Access denied")

    history = db.query(models.EventHistory).filter_by(event_id=event_id).order_by(models.EventHistory.timestamp.desc()).all()
    return history

# ---------- Get Specific Version ----------
@router.get("/{event_id}/history/{version_id}", response_model=schemas.EventHistoryOut)
def get_version(event_id: int, version_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission:
        raise HTTPException(status_code=403, detail="Access denied")

    version = db.query(models.EventHistory).filter_by(id=version_id, event_id=event_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return version

# ---------- Rollback to Previous Version ----------
@router.post("/{event_id}/rollback/{version_id}", response_model=schemas.EventOut)
def rollback_event(event_id: int, version_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission or permission.role not in ("Owner", "Editor"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    version = db.query(models.EventHistory).filter_by(id=version_id, event_id=event_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    event = db.query(models.Event).filter_by(id=event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Save current state
    backup = models.EventHistory(
        event_id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        recurrence_pattern=event.recurrence_pattern,
        changed_by=current_user.id
    )
    db.add(backup)

    # Restore
    event.title = version.title
    event.description = version.description
    event.start_time = version.start_time
    event.end_time = version.end_time
    event.location = version.location
    event.recurrence_pattern = version.recurrence_pattern

    db.commit()
    db.refresh(event)
    return event

# ---------- Get Field-by-Field Diff ----------
@router.get("/{event_id}/diff/{v1}/{v2}", response_model=List[schemas.DiffResponse])
def get_diff(event_id: int, v1: int, v2: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    permission = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not permission:
        raise HTTPException(status_code=403, detail="Access denied")

    version1 = db.query(models.EventHistory).filter_by(id=v1, event_id=event_id).first()
    version2 = db.query(models.EventHistory).filter_by(id=v2, event_id=event_id).first()

    if not version1 or not version2:
        raise HTTPException(status_code=404, detail="One or both versions not found")

    fields = ["title", "description", "start_time", "end_time", "location", "recurrence_pattern"]
    diff_list = []

    for field in fields:
        old = getattr(version1, field)
        new = getattr(version2, field)
        if old != new:
            diff_list.append({
                "field": field,
                "old_value": str(old),
                "new_value": str(new)
            })

    return diff_list
