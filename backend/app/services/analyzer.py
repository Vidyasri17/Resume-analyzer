import re, json, os
from .skill_normalizer import normalize_list, categorize
from .scoring import extract_years, calc_scores
from .course_recommender import build_recommendations

ALL_SKILLS = [
 "python","java","javascript","typescript","react","vue","angular","next.js","node.js","express","spring boot",
 "django","flask","fastapi","html","css","tailwind css","redux","postgresql","mysql","mongodb","redis","sql","sqlite",
 "aws","azure","google cloud","docker","kubernetes","ci/cd","jenkins","terraform","linux","git","graphql","rest apis",
 "machine learning","artificial intelligence","tensorflow","pytorch","scikit-learn","nlp","deep learning","data science",
 "numpy","pandas","android","ios","flutter","react native","kotlin","swift","go","ruby on rails","php","c#",".net",
 "microservices","agile","scrum","figma","jira","oracle","dynamodb","cassandra","elasticsearch"
]
EDU_KEYWORDS=["bachelor","master","phd","b.tech","m.tech","b.e","m.e","bca","mca","degree","university","college"]
CERT_KEYWORDS=["aws certified","azure certified","certified","certification","pmp","scrum master","google cloud certified","kubernetes certified","oracle certified"]

def extract_skills(text):
    low=text.lower()
    found=[]
    for s in ALL_SKILLS:
        pattern = r'\b' + re.escape(s) + r'\b'
        if re.search(pattern, low):
            found.append(s)
    return normalize_list(found)

def extract_keywords(text):
    words=re.findall(r'\b[a-z]{4,}\b', text.lower())
    freq={}
    for w in words:
        if w in ["with","have","this","that","will","from","your","about","role","team","work","experience","years","skills","ability","knowledge","including","using","within","should","required"]: continue
        freq[w]=freq.get(w,0)+1
    sorted_words=sorted(freq.items(), key=lambda x: -x[1])
    return [w for w,_ in sorted_words[:15]]

def extract_education(text):
    low=text.lower()
    found=[k for k in EDU_KEYWORDS if k in low]
    edu_snippet=""
    for line in text.split("\n"):
        if any(k in line.lower() for k in ["education","university","college","bachelor","master","degree"]):
            edu_snippet+=line+" "
    return edu_snippet.strip()[:500] if edu_snippet else (" ".join(found) if found else "Not identified in the resume")

def extract_certs(text):
    low=text.lower()
    found=[]
    for c in CERT_KEYWORDS:
        if c in low:
            found.append(c)
    extra=[]
    for line in text.split("\n"):
        if "certif" in line.lower():
            extra.append(line.strip()[:80])
    return normalize_list(found) if found else []

def try_llm(jd_text, resume_texts):
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base=os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client=OpenAI(api_key=api_key, base_url=base)
        results=[]
        for idx, rtext in enumerate(resume_texts):
            prompt=f"""You are an ATS analyzer. Return STRICT JSON only.
JD:
{jd_text[:6000]}

Resume {idx+1}:
{rtext[:6000]}

Return JSON with keys:
jd_skills_required: string[] (max 15 critical skills)
jd_skills_preferred: string[] (bonus skills)
jd_certs: string[] 
jd_keywords: string[] (10 keywords)
resume_skills: string[] (all skills found in resume)
resume_certs: string[]
resume_education: string (short)
Do not hallucinate. Only skills present in text.
"""
            resp=client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=0, response_format={"type":"json_object"})
            content=resp.choices[0].message.content
            data=json.loads(content)
            results.append(data)
        return results
    except Exception as e:
        print("LLM fallback:",e)
        return None

def analyze(jd_text, resume_texts, filenames):
    jd_text = jd_text[:20000]
    llm_data = try_llm(jd_text, resume_texts)

    jd_skills_all=[]
    jd_required=[]
    jd_preferred=[]
    jd_certs=[]
    jd_keywords=[]

    if llm_data and len(llm_data)==len(resume_texts):
        first=llm_data[0]
        jd_required=first.get("jd_skills_required",[])
        jd_preferred=first.get("jd_skills_preferred",[])
        jd_certs=first.get("jd_certs",[])
        jd_keywords=first.get("jd_keywords",[])
        jd_skills_all=normalize_list(jd_required+jd_preferred)
        if not jd_skills_all:
            jd_skills_all=extract_skills(jd_text)
            jd_required=jd_skills_all[:8]
    else:
        jd_skills_all=extract_skills(jd_text)
        jd_required=jd_skills_all[: max(5, len(jd_skills_all)*2//3)]
        jd_preferred=jd_skills_all[len(jd_required):]
        jd_certs=extract_certs(jd_text)
        jd_keywords=extract_keywords(jd_text)

    jd_exp_years=extract_years(jd_text)
    jd_edu=extract_education(jd_text)

    results=[]
    for i, rtext in enumerate(resume_texts):
        fname=filenames[i]
        rtext=rtext[:20000]
        if llm_data:
            ld=llm_data[i]
            resume_skills=normalize_list(ld.get("resume_skills", extract_skills(rtext)))
            resume_certs_llm=normalize_list(ld.get("resume_certs",[]))
            resume_edu_llm=ld.get("resume_education","")
        else:
            resume_skills=extract_skills(rtext)
            resume_certs_llm=extract_certs(rtext)
            resume_edu_llm=extract_education(rtext)

        resume_exp_years=extract_years(rtext)
        resume_edu = resume_edu_llm if resume_edu_llm else extract_education(rtext)
        resume_certs = resume_certs_llm if resume_certs_llm else extract_certs(rtext)

        jd_skills_n=normalize_list(jd_skills_all)
        resume_skills_n=normalize_list(resume_skills)
        jd_set=set(jd_skills_n)
        resume_set=set(resume_skills_n)
        matching=sorted(jd_set & resume_set)
        missing_required=sorted(set(normalize_list(jd_required)) - resume_set)
        missing_preferred=sorted(set(normalize_list(jd_preferred)) - resume_set)
        if not jd_required:
            missing_required=sorted(jd_set - resume_set)
            missing_preferred=[]

        scores=calc_scores(jd_skills_all, resume_skills, jd_exp_years, resume_exp_years, [jd_edu], resume_edu, jd_keywords, rtext, jd_certs, resume_certs)

        strengths=[]
        if matching:
            strengths.append(f"Strong match on {', '.join(matching[:4])}")
        if scores["experience_score"]>=75:
            strengths.append(f"Experience aligns with JD requirement ({resume_exp_years or 'relevant'} years)")
        if not strengths:
            strengths.append("Resume shows some relevant background but limited direct skill overlap")

        gaps=[]
        if missing_required:
            gaps.append(f"Missing required skills: {', '.join(missing_required[:5])} — not identified in the resume")
        if missing_preferred:
            gaps.append(f"Missing preferred skills: {', '.join(missing_preferred[:3])}")
        if scores["experience_score"]<50 and jd_exp_years:
            gaps.append(f"Experience gap: JD expects {jd_exp_years} years, resume indicates {resume_exp_years or 0}")

        recs=build_recommendations(missing_required[:5], missing_preferred[:3])

        why=f"Score {scores['overall_score']}/100: {scores['matched_count']}/{scores['total_jd_skills']} JD skills matched ({scores['skill_match_score']}%). Experience {scores['experience_score']}%, Education {scores['education_score']}%, Keywords {scores['keyword_score']}%, Certs {scores['certification_score']}%."
        categorized=categorize(resume_skills_n)

        results.append({
            "candidate_name": fname.rsplit(".",1)[0][:30] or f"Candidate {i+1}",
            "filename": fname,
            "ats_score": scores["overall_score"],
            "score_breakdown": {
                "skills": scores["skill_match_score"],
                "experience": scores["experience_score"],
                "education": scores["education_score"],
                "keywords": scores["keyword_score"],
                "certifications": scores["certification_score"]
            },
            "matching_skills": matching,
            "missing_required_skills": missing_required,
            "missing_preferred_skills": missing_preferred,
            "all_resume_skills": resume_skills_n,
            "categorized_skills": categorized,
            "strengths": strengths,
            "gaps": gaps,
            "course_recommendations": recs,
            "experience_years": resume_exp_years,
            "education_summary": resume_edu[:300],
            "why_score": why,
            "jd_exp_years": jd_exp_years
        })

    results_sorted=sorted(results, key=lambda x: -x["ats_score"])
    for idx,r in enumerate(results_sorted):
        r["rank"]=idx+1

    summary={
        "candidates_analyzed": len(results),
        "top_candidate": results_sorted[0]["candidate_name"] if results_sorted else None,
        "highest_score": results_sorted[0]["ats_score"] if results_sorted else 0,
        "average_score": int(sum(r["ats_score"] for r in results)/len(results)) if results else 0,
        "jd_skills": jd_skills_all,
        "jd_required": jd_required,
        "jd_preferred": jd_preferred,
        "ranking": [{"rank":r["rank"],"candidate_name":r["candidate_name"],"score":r["ats_score"]} for r in results_sorted]
    }
    return {"summary": summary, "results": results_sorted}
