from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from . import models, schemas, database, utils
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Register --------
@router.post("/register", response_model=schemas.UserOut)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pw = utils.hash_password(user_data.password)
    user = models.User(username=user_data.username, email=user_data.email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# -------- Login --------
@router.post("/login", response_model=dict)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token_data = {"sub": user.username}
    access_token = utils.create_access_token(token_data)
    refresh_token = utils.create_refresh_token(token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# -------- Refresh Token --------
@router.post("/refresh")
def refresh_token(refresh_token: str = Body(...)):
    try:
        payload = utils.decode_token(refresh_token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = utils.create_access_token({"sub": username})
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token expired or invalid")

# -------- Logout --------
@router.post("/logout")
def logout(request: Request, token: str = Depends(oauth2_scheme)):
    if utils.is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Already logged out")
    utils.blacklist_token(token)
    return {"message": "Logged out successfully"}

# -------- Get Current User --------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    if utils.is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    payload = utils.decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

