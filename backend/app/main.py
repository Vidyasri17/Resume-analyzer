from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routes.analyze import router as analyze_router
from .routes.chat import router as chat_router

load_dotenv()

app=FastAPI(title="AI Resume ATS Analyzer", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root(): return {"message":"AI Resume ATS Analyzer API","health":"/api/health"}

@app.get("/api/health")
def health(): return {"status":"ok"}

app.include_router(analyze_router, prefix="/api", tags=["analyze"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
