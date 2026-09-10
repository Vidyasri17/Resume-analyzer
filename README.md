# AI Resume ATS Analyzer

Compare multiple resumes against a JD with explainable ATS scoring (0-100) + chatbot.

## Stack
- **Frontend:** React + Vite
- **Backend:** Python FastAPI, pypdf, python-docx, openai (optional)
- No API key required — deterministic local scoring works offline. If `OPENAI_API_KEY` is set, JD/resume skill extraction is enhanced via LLM.

## Scoring (explainable)
- Skills 50% | Experience 20% | Education 10% | Keywords 10% | Certs 10%
- Skill aliases normalized (ReactJS→React, Postgres→PostgreSQL, ML→Machine Learning, etc.)
- `overall = 0.5*skills + 0.2*exp + 0.1*edu + 0.1*kw + 0.1*cert`

## Run locally
### Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
# health: http://localhost:8000/api/health
```

### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
# http://localhost:5173
```
Vite proxies `/api` → `http://localhost:8000` (see `vite.config.js`).

### Env (optional)
Copy `.env.example` → `.env` and set `OPENAI_API_KEY` to enable LLM-enhanced extraction & chat. Without it, everything works locally.

## API
### POST /api/analyze
Form-data: `jd` (file), `resumes` (2–10 files, pdf/docx/txt)
```json
{
  "summary": { "candidates_analyzed": 3, "top_candidate": "alice", "highest_score": 87, "average_score": 72, "ranking": [...] },
  "results": [{ "candidate_name":"alice","ats_score":87,"score_breakdown":{"skills":90,"experience":75,"education":100,"keywords":80,"certifications":60},"matching_skills":["react","aws"],"missing_required_skills":["docker"],"missing_preferred_skills":["redis"],"course_recommendations":[{ "skill":"docker","priority":"High","recommendations":[{ "title":"Docker Get Started","platform":"Docker","url":"https://docs.docker.com/get-started/"}]}]}]
}
```

### POST /api/chat
```json
{ "message":"Which candidate is best?", "analysis": { "<same as /analyze response>" } }
```
Returns `{ "answer": "..." }`. Uses LLM if configured, else rule-based.

## Project structure
```
backend/app/
  main.py
  routes/analyze.py, chat.py
  services/document_extractor.py, analyzer.py, scoring.py, skill_normalizer.py, course_recommender.py
  models/schemas.py
frontend/src/App.jsx
```

## Testing
Upload 1 JD + 2 resumes in UI. Verify ranking, score breakdown, matching/missing tags, course cards, and chatbot (try “Why did Candidate 2 score lower?”).
Backend unit: document extraction tested via manual upload; scoring deterministic.

## Notes
- Handles multi-page PDFs, DOCX tables/bullets.
- Never hallucinates skills — only reports skills found in text; missing = “Not identified in the resume”.
- Course URLs are real (official docs / Coursera / AWS etc.); fallback shows title+platform if offline.
