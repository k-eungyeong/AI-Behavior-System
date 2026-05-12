from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    upload,
    analysis,
    history,
    realtime,
    auth,
    admin,
    rag,
    cctv
)
from app.database.connection import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Behavior Analysis Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(realtime.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(rag.router)
app.include_router(cctv.router)


@app.get("/")
def root():
    return {"message": "Server is running"}