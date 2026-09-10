import re
from .skill_normalizer import normalize_list

def extract_years(text:str)->float:
    patterns=[
        r'(\d+)\+?\s*years? of experience',
        r'(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?',
        r'experience.*?(\d+)\s*years?',
    ]
    years=[]
    low=text.lower()
    for pat in patterns:
        for m in re.finditer(pat, low):
            try: years.append(int(m.group(1)))
            except: pass
    return max(years) if years else 0

def keyword_score(jd_keywords, resume_text):
    if not jd_keywords: return 100
    rt = resume_text.lower()
    matched = sum(1 for k in jd_keywords if k.lower() in rt)
    return int(matched/len(jd_keywords)*100)

def calc_scores(jd_skills, resume_skills, jd_exp_years, resume_exp_years, jd_edu, resume_edu, jd_keywords, resume_text, jd_certs, resume_certs):
    jd_skills_n = normalize_list(jd_skills)
    resume_skills_n = normalize_list(resume_skills)
    total = len(jd_skills_n) or 1
    matched = len(set(jd_skills_n) & set(resume_skills_n))
    skill_score = int(matched/total*100)

    if jd_exp_years==0:
        exp_score=80 if resume_exp_years>0 else 60
    else:
        if resume_exp_years>=jd_exp_years: exp_score=100
        elif resume_exp_years>=jd_exp_years*0.7: exp_score=75
        elif resume_exp_years>=jd_exp_years*0.5: exp_score=55
        elif resume_exp_years>0: exp_score=35
        else: exp_score=30

    if not jd_edu:
        edu_score=80
    else:
        edu_score=100 if any(e.lower() in resume_edu.lower() for e in jd_edu) else 40
        if "bachelor" in resume_edu.lower() or "master" in resume_edu.lower() or "phd" in resume_edu.lower():
            if edu_score<40: edu_score=50

    kw_score = keyword_score(jd_keywords, resume_text)

    if not jd_certs:
        cert_score=70
    else:
        jd_c = normalize_list(jd_certs)
        rc = normalize_list(resume_certs)
        if not jd_c: cert_score=70
        else:
            m=len(set(jd_c)&set(rc))
            cert_score=int(m/len(jd_c)*100) if jd_c else 70
            if cert_score==0: cert_score=30

    overall = int(skill_score*0.5 + exp_score*0.2 + edu_score*0.1 + kw_score*0.1 + cert_score*0.1)
    return {
        "overall_score": overall,
        "skill_match_score": skill_score,
        "experience_score": exp_score,
        "education_score": edu_score,
        "keyword_score": kw_score,
        "certification_score": cert_score,
        "matched_count": matched,
        "total_jd_skills": total
    }
