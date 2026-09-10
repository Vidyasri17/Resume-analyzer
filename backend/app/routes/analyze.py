from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ..services.document_extractor import extract_text, clean_text
from ..services.analyzer import analyze

router=APIRouter()

@router.post("/analyze")
async def analyze_resumes(jd: UploadFile = File(...), resumes: List[UploadFile] = File(...)):
    if not jd:
        raise HTTPException(400,"JD file is required")
    if len(resumes)<1:
        raise HTTPException(400,"At least 1 resume is required")

    for f in [jd]+resumes:
        if f.size and f.size>10*1024*1024:
            raise HTTPException(400,f"File too large (max 10MB): {f.filename}")

    try:
        jd_content=await jd.read()
        jd_text=clean_text(extract_text(jd.filename, jd_content))
    except Exception as e:
        raise HTTPException(400,f"Failed to extract JD: {str(e)}")
    if len(jd_text)<50:
        raise HTTPException(400,"JD file appears empty or too short")

    resume_texts=[]
    filenames=[]
    errors=[]
    for r in resumes:
        try:
            content=await r.read()
            text=clean_text(extract_text(r.filename, content))
            if len(text)<50:
                errors.append(f"{r.filename}: file appears empty")
                continue
            resume_texts.append(text)
            filenames.append(r.filename)
        except Exception as e:
            errors.append(f"{r.filename}: {str(e)}")

    if len(resume_texts)<1:
        raise HTTPException(400,"Need at least 1 valid resume. Errors: "+"; ".join(errors))
    
    try:
        result=analyze(jd_text, resume_texts, filenames)
        if errors:
            result["warnings"]=errors
        return result
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")
