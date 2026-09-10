from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ScoreBreakdown(BaseModel):
    skills: int
    experience: int
    education: int
    keywords: int
    certifications: int

class CourseRec(BaseModel):
    title: str
    platform: str
    level: Optional[str]=None
    url: Optional[str]=None

class Recommendation(BaseModel):
    skill: str
    priority: str
    reason: str
    recommendations: List[CourseRec]

class CandidateResult(BaseModel):
    candidate_name: str
    filename: str
    ats_score: int
    score_breakdown: ScoreBreakdown
    matching_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    all_resume_skills: List[str]
    categorized_skills: Dict[str, List[str]]
    strengths: List[str]
    gaps: List[str]
    course_recommendations: List[Recommendation]
    experience_years: int
    education_summary: str
    why_score: str
    rank: int

class Summary(BaseModel):
    candidates_analyzed: int
    top_candidate: Optional[str]
    highest_score: int
    average_score: int
    jd_skills: List[str]
    jd_required: List[str]
    jd_preferred: List[str]
    ranking: List[Dict[str, Any]]

class AnalyzeResponse(BaseModel):
    summary: Summary
    results: List[CandidateResult]

class ChatRequest(BaseModel):
    message: str
    analysis: Dict[str, Any]

class ChatResponse(BaseModel):
    answer: str
