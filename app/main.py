from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, database
from .auth import router as auth_router
from .events import router as event_router
from .permissions import router as permission_router
from .history import router as history_router

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="NeoFi Collaborative Event Management API",
    description="A FastAPI backend for event collaboration with roles, versioning, and history.",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(permission_router)
app.include_router(history_router)

@app.get("/")
def root():
    return {"message": "Welcome to the NeoFi Event Management Backend"}
