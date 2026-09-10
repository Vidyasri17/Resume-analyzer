ALIASES = {
    "reactjs": "react",
    "react.js": "react",
    "react js": "react",
    "node.js": "node.js",
    "nodejs": "node.js",
    "node": "node.js",
    "postgres": "postgresql",
    "postgress": "postgresql",
    "postgre sql": "postgresql",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "js": "javascript",
    "ts": "typescript",
    "k8s": "kubernetes",
    "gcp": "google cloud",
    "rest api": "rest apis",
    "restapi": "rest apis",
    "restful api": "rest apis",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
}

CATEGORIES = {
    "Frontend": ["react","javascript","typescript","html","css","vue","angular","next.js","tailwind css","redux"],
    "Backend": ["node.js","express","java","spring boot","python","django","flask","fastapi","go","ruby on rails","php","c#",".net"],
    "Database": ["postgresql","mysql","mongodb","redis","sql","sqlite","oracle","dynamodb","cassandra","elasticsearch"],
    "Cloud/DevOps": ["aws","azure","google cloud","docker","kubernetes","ci/cd","jenkins","terraform","linux","git"],
    "AI/ML": ["machine learning","artificial intelligence","tensorflow","pytorch","scikit-learn","nlp","deep learning","data science","numpy","pandas"],
    "Mobile": ["android","ios","flutter","react native","kotlin","swift"],
    "Other": ["graphql","rest apis","microservices","agile","scrum","figma","jira"]
}

SKILL_CANONICAL = set()
for v in CATEGORIES.values():
    SKILL_CANONICAL.update(v)
SKILL_CANONICAL.update(ALIASES.values())
SKILL_CANONICAL = sorted(SKILL_CANONICAL)

def normalize(skill: str) -> str:
    s = skill.strip().lower()
    s = s.replace("  "," ").strip()
    return ALIASES.get(s, s)

def normalize_list(skills):
    seen={}
    for s in skills:
        n=normalize(s)
        seen[n]=True
    return sorted(seen.keys())

def categorize(skills):
    out={}
    for cat, lst in CATEGORIES.items():
        matched=[s for s in skills if s in lst]
        if matched:
            out[cat]=matched
    other=[s for s in skills if not any(s in v for v in CATEGORIES.values())]
    if other:
        out["Other"]=other
    return out
