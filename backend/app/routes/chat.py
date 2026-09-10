from fastapi import APIRouter
from ..models.schemas import ChatRequest, ChatResponse
import os, json, re

router=APIRouter()

def local_answer(message: str, analysis: dict)->str:
    msg=message.lower()
    results=analysis.get("results",[])
    summary=analysis.get("summary",{})
    if not results:
        return "No analysis data available. Please analyze resumes first."

    def find_candidate(q):
        for r in results:
            if r["candidate_name"].lower() in q or r["filename"].lower() in q:
                return r
        m=re.search(r'candidate\s*(\d+)',q)
        if m:
            idx=int(m.group(1))-1
            if 0<=idx<len(results): return results[idx]
        return None

    if any(k in msg for k in ["best","top","highest","rank","should i interview","hire"]):
        top=results[0]
        return f"**{top['candidate_name']}** is the best match with **{top['ats_score']}/100** (Rank #{top['rank']}). Matching skills: {', '.join(top['matching_skills'][:5]) or 'limited'}. Missing: {', '.join(top['missing_required_skills'][:4]) or 'none major'}. Ranking: " + ", ".join([f"{r['candidate_name']} ({r['ats_score']})" for r in results])

    if "missing" in msg or "learn" in msg or "gap" in msg:
        cand=find_candidate(msg)
        if cand:
            return f"**{cand['candidate_name']}** missing required: {', '.join(cand['missing_required_skills']) or 'none'}; missing preferred: {', '.join(cand['missing_preferred_skills']) or 'none'}. Gaps: {'; '.join(cand['gaps'])} Recommendation: {cand['course_recommendations'][0]['skill'] if cand['course_recommendations'] else 'N/A'} -> {cand['course_recommendations'][0]['recommendations'][0]['title'] if cand['course_recommendations'] else ''}"
        else:
            all_missing=set()
            for r in results: all_missing.update(r['missing_required_skills'])
            return f"Across candidates, commonly missing: {', '.join(list(all_missing)[:6])}. Details per candidate: " + " | ".join([f"{r['candidate_name']}: {', '.join(r['missing_required_skills'][:3]) or 'none'}" for r in results])

    if "why" in msg or "score" in msg or "lower" in msg:
        cand=find_candidate(msg)
        if cand:
            return f"**{cand['candidate_name']}** scored **{cand['ats_score']}/100**. Breakdown: Skills {cand['score_breakdown']['skills']}%, Experience {cand['score_breakdown']['experience']}%, Education {cand['score_breakdown']['education']}%, Keywords {cand['score_breakdown']['keywords']}%, Certs {cand['score_breakdown']['certifications']}%. {cand['why_score']} Gaps: {'; '.join(cand['gaps'])}"
        else:
            return "Scores: " + ", ".join([f"{r['candidate_name']} {r['ats_score']}/100 ({r['why_score'][:80]}...)" for r in results])

    if any(s in msg for s in ["java","python","react","aws","docker","skill"]):
        skill_match=[w for w in msg.split() if len(w)>2]
        best=None; best_count=0
        for r in results:
            count=sum(1 for w in skill_match if w in " ".join(r['all_resume_skills']).lower() or w in " ".join(r['matching_skills']).lower())
            if count>best_count: best=r; best_count=count
        if best and best_count>0:
            return f"For your query, **{best['candidate_name']}** has strongest relevant skills: {', '.join(best['matching_skills'][:6])}. All its skills: {', '.join(best['all_resume_skills'][:8])}. Missing: {', '.join(best['missing_required_skills'][:3]) or 'none'}"
        else:
            return "Comparison of skills: " + " | ".join([f"{r['candidate_name']}: {', '.join(r['matching_skills'][:4]) or 'no direct matches'}" for r in results])

    if "compare" in msg or "vs" in msg or "versus" in msg or "difference" in msg:
        return "Candidate comparison:\n" + "\n".join([f"- **{r['candidate_name']}** ({r['ats_score']}/100): matching [{', '.join(r['matching_skills'][:4]) or 'none'}], missing [{', '.join(r['missing_required_skills'][:3]) or 'none'}], experience {r['experience_years']} yrs" for r in results])

    cand=find_candidate(msg)
    if cand:
        return f"**{cand['candidate_name']}** — {cand['ats_score']}/100. Strengths: {'; '.join(cand['strengths'])}. Gaps: {'; '.join(cand['gaps'])}. {cand['why_score']}"

    return f"Analyzed {summary.get('candidates_analyzed',len(results))} candidates. Top: {summary.get('top_candidate')} ({summary.get('highest_score')}/100), avg {summary.get('average_score')}/100. Ask: 'Which candidate is best?', 'Why did Candidate 1 get lower?', 'What is missing from Candidate 2?', 'Compare candidates'."

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    msg=req.message.strip()
    if not msg:
        return ChatResponse(answer="Please ask a question about the candidates.")
    analysis=req.analysis or {}
    # Try LLM if available
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            base=os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
            model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
            client=OpenAI(api_key=api_key, base_url=base)
            ctx=json.dumps(analysis)[:8000]
            prompt=f"You are a helpful ATS assistant. Use ONLY the analysis JSON. Never invent skills. Analysis:\n{ctx}\n\nUser question: {msg}\nAnswer concisely, grounded in data. Use markdown."
            resp=client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=0.2, max_tokens=600)
            return ChatResponse(answer=resp.choices[0].message.content)
        except Exception as e:
            print("chat llm fallback",e)
    answer=local_answer(msg, analysis)
    return ChatResponse(answer=answer)
