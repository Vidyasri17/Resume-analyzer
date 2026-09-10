COURSES = {
    "react": [{"title":"React Official Docs - Learn React","platform":"React.dev","level":"Beginner","url":"https://react.dev/learn"},{"title":"React - The Complete Guide","platform":"Udemy","level":"Beginner"}],
    "node.js": [{"title":"Node.js Official Learn","platform":"Node.js","level":"Beginner","url":"https://nodejs.org/en/learn"},{"title":"Node.js Complete Course","platform":"freeCodeCamp","level":"Beginner","url":"https://www.freecodecamp.org"}],
    "docker": [{"title":"Docker Get Started","platform":"Docker","level":"Beginner","url":"https://docs.docker.com/get-started/"},{"title":"Docker for Beginners","platform":"Udemy","level":"Beginner"}],
    "kubernetes": [{"title":"Kubernetes Basics","platform":"Kubernetes","level":"Intermediate","url":"https://kubernetes.io/docs/tutorials/kubernetes-basics/"}],
    "aws": [{"title":"AWS Cloud Practitioner Essentials","platform":"AWS Skill Builder","level":"Beginner","url":"https://skillbuilder.aws/"}],
    "azure": [{"title":"Azure Fundamentals AZ-900","platform":"Microsoft Learn","level":"Beginner","url":"https://learn.microsoft.com/en-us/certifications/azure-fundamentals/"}],
    "google cloud": [{"title":"Google Cloud Skills Boost","platform":"Google Cloud","level":"Beginner","url":"https://www.cloudskillsboost.google/"}],
    "python": [{"title":"Python for Everybody","platform":"Coursera","level":"Beginner","url":"https://www.coursera.org/specializations/python"}],
    "java": [{"title":"Java Programming Masterclass","platform":"Udemy","level":"Beginner"}],
    "spring boot": [{"title":"Spring Boot Official Guides","platform":"Spring.io","level":"Intermediate","url":"https://spring.io/guides"}],
    "postgresql": [{"title":"PostgreSQL Tutorial","platform":"PostgreSQL","level":"Beginner","url":"https://www.postgresql.org/docs/"}],
    "mysql": [{"title":"MySQL Tutorial","platform":"MySQL","level":"Beginner","url":"https://dev.mysql.com/doc/"}],
    "mongodb": [{"title":"MongoDB University","platform":"MongoDB","level":"Beginner","url":"https://learn.mongodb.com/"}],
    "redis": [{"title":"Redis University","platform":"Redis","level":"Beginner","url":"https://university.redis.com/"}],
    "machine learning": [{"title":"Machine Learning by Andrew Ng","platform":"Coursera","level":"Beginner","url":"https://www.coursera.org/learn/machine-learning"}],
    "artificial intelligence": [{"title":"AI For Everyone","platform":"Coursera","level":"Beginner","url":"https://www.coursera.org/learn/ai-for-everyone"}],
    "tensorflow": [{"title":"TensorFlow Developer Certificate","platform":"TensorFlow","level":"Intermediate","url":"https://www.tensorflow.org/learn"}],
    "pytorch": [{"title":"PyTorch Tutorials","platform":"PyTorch","level":"Intermediate","url":"https://pytorch.org/tutorials/"}],
    "typescript": [{"title":"TypeScript Handbook","platform":"TypeScript","level":"Beginner","url":"https://www.typescriptlang.org/docs/handbook"}],
    "javascript": [{"title":"JavaScript Algorithms and Data Structures","platform":"freeCodeCamp","level":"Beginner","url":"https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"}],
    "graphql": [{"title":"GraphQL Official Learn","platform":"GraphQL","level":"Beginner","url":"https://graphql.org/learn/"}],
    "terraform": [{"title":"Terraform Get Started","platform":"HashiCorp","level":"Beginner","url":"https://developer.hashicorp.com/terraform/tutorials"}],
    "ci/cd": [{"title":"CI/CD with GitHub Actions","platform":"GitHub","level":"Beginner","url":"https://docs.github.com/en/actions"}],
    "rest apis": [{"title":"REST API Tutorial","platform":"RESTfulAPI.net","level":"Beginner","url":"https://restfulapi.net/"}],
    "microservices": [{"title":"Microservices Architecture","platform":"Microsoft Learn","level":"Intermediate","url":"https://learn.microsoft.com/en-us/azure/architecture/microservices/"}],
}

DEFAULT_COURSE = [{"title":"Official Documentation & Hands-on Practice","platform":"Official Docs","level":"Beginner"}]

def recommend(skill: str):
    key = skill.lower().strip()
    return COURSES.get(key, DEFAULT_COURSE)

def build_recommendations(missing_required, missing_preferred):
    out=[]
    for s in missing_required:
        out.append({"skill": s, "priority":"High", "reason": f"{s} is explicitly mentioned as a required skill in the JD.", "recommendations": recommend(s)})
    for s in missing_preferred:
        out.append({"skill": s, "priority":"Medium", "reason": f"{s} is a preferred/bonus skill in the JD.", "recommendations": recommend(s)})
    return out
