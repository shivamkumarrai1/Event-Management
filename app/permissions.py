from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database, auth

router = APIRouter(prefix="/api/events", tags=["Permissions"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------- Share Event with Users -------------
@router.post("/{event_id}/share", response_model=List[schemas.PermissionOut])
def share_event(event_id: int, share_data: List[schemas.ShareUser], db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Ensure current user is Owner
    owner_perm = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id, role="Owner").first()
    if not owner_perm:
        raise HTTPException(status_code=403, detail="Only owner can share event")

    result = []
    for item in share_data:
        # Prevent duplicate sharing
        perm = db.query(models.Permission).filter_by(user_id=item.user_id, event_id=event_id).first()
        if perm:
            perm.role = item.role
        else:
            perm = models.Permission(user_id=item.user_id, event_id=event_id, role=item.role)
            db.add(perm)
        result.append(perm)

    db.commit()
    return result

# ------------- List Permissions for Event -------------
@router.get("/{event_id}/permissions", response_model=List[schemas.PermissionOut])
def list_permissions(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Check if user has access
    perm = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not perm:
        raise HTTPException(status_code=403, detail="Permission denied")

    return db.query(models.Permission).filter_by(event_id=event_id).all()

# ------------- Update User Role -------------
@router.put("/{event_id}/permissions/{user_id}", response_model=schemas.PermissionOut)
def update_permission(event_id: int, user_id: int, data: schemas.ShareUser, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Only owner can update
    owner_perm = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id, role="Owner").first()
    if not owner_perm:
        raise HTTPException(status_code=403, detail="Only owner can update permissions")

    perm = db.query(models.Permission).filter_by(user_id=user_id, event_id=event_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    perm.role = data.role
    db.commit()
    return perm

# ------------- Remove User Access -------------
@router.delete("/{event_id}/permissions/{user_id}", status_code=204)
def remove_permission(event_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Only owner can revoke access
    owner_perm = db.query(models.Permission).filter_by(user_id=current_user.id, event_id=event_id, role="Owner").first()
    if not owner_perm:
        raise HTTPException(status_code=403, detail="Only owner can remove permissions")

    perm = db.query(models.Permission).filter_by(user_id=user_id, event_id=event_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(perm)
    db.commit()
