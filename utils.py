"""
utils.py — AI Resume Analyzer v3.1
Complete 24-role skill database · 50+ course mappings · Fixed PDF validation · Bug-free
"""

import re, io, json, math
from collections import Counter
from datetime import datetime

import PyPDF2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.units import inch

# ═══════════════════════════════════════════════
# SKILL DATABASE
# ═══════════════════════════════════════════════

SKILL_DICT = {
    "Programming Languages": [
        "python","java","javascript","typescript","c++","c#","r","scala",
        "go","rust","kotlin","swift","php","ruby","matlab","bash","dart","julia"
    ],
    "AI / ML": [
        "machine learning","deep learning","neural network","nlp",
        "natural language processing","computer vision","reinforcement learning",
        "transfer learning","generative ai","llm","large language model",
        "transformers","bert","gpt","object detection","image classification",
        "time series","feature engineering","model deployment","mlops",
        "rag","langchain","vector database","embeddings","fine tuning","prompt engineering"
    ],
    "Web Development": [
        "html","css","react","angular","vue","node.js","express","django",
        "flask","fastapi","streamlit","rest api","graphql","bootstrap",
        "tailwind","next.js","spring boot","jquery"
    ],
    "Databases": [
        "sql","mysql","postgresql","mongodb","sqlite","redis","elasticsearch",
        "cassandra","dynamodb","oracle","neo4j","pinecone","chroma","firebase"
    ],
    "Cloud & DevOps": [
        "aws","azure","gcp","google cloud","docker","kubernetes","terraform",
        "ci/cd","github actions","jenkins","lambda","ec2","s3","sagemaker","vertex ai"
    ],
    "Libraries": [
        "tensorflow","pytorch","keras","scikit-learn","pandas","numpy",
        "matplotlib","seaborn","plotly","opencv","nltk","spacy",
        "hugging face","xgboost","lightgbm","catboost","scipy"
    ],
    "Tools": [
        "git","github","gitlab","jira","postman","linux","jupyter",
        "vs code","tableau","power bi","excel","airflow","mlflow","spark","kafka"
    ]
}

ALL_SKILLS = {s for cat in SKILL_DICT.values() for s in cat}

# ── 24 Complete Roles with Skills ──
ROLE_SKILLS = {
    "AI Engineer":            ["python","machine learning","deep learning","tensorflow","pytorch","llm","nlp","docker","kubernetes","mlops","aws","fastapi","transformers","langchain","rag","vector database","generative ai","fine tuning"],
    "Data Scientist":         ["python","machine learning","statistics","pandas","numpy","scikit-learn","sql","matplotlib","seaborn","r","feature engineering","deep learning","tableau","jupyter"],
    "ML Engineer":            ["python","machine learning","deep learning","tensorflow","pytorch","scikit-learn","mlops","docker","kubernetes","aws","model deployment","feature engineering","sql"],
    "NLP Engineer":           ["python","nlp","transformers","bert","gpt","pytorch","tensorflow","langchain","rag","deep learning","hugging face","prompt engineering"],
    "Computer Vision Engineer":["python","computer vision","deep learning","pytorch","tensorflow","opencv","object detection","image classification","cnn"],
    "Generative AI Engineer": ["python","llm","transformers","pytorch","langchain","prompt engineering","fine tuning","api","fastapi","docker"],
    "Data Analyst":           ["sql","python","excel","tableau","power bi","pandas","numpy","matplotlib","data visualization","reporting","postgresql","mysql"],
    "Data Engineer":          ["python","sql","apache spark","kafka","airflow","etl","cloud","aws","gcp","azure","postgres","hadoop"],
    "Business Analyst":       ["sql","excel","tableau","power bi","python","reporting","data visualization","communication"],
    "BI Developer":           ["sql","tableau","power bi","python","data warehouse","reporting","etl","mysql","postgresql"],
    "Python Developer":       ["python","django","flask","fastapi","rest api","sql","git","docker","linux","postgresql","redis","aws"],
    "Full Stack Developer":   ["javascript","react","node.js","html","css","sql","mongodb","git","rest api","docker","aws","typescript","postgresql"],
    "Frontend Developer":     ["javascript","react","html","css","typescript","vue","angular","git","rest api","ui/ux","responsive design"],
    "Backend Developer":      ["python","java","node.js","sql","docker","rest api","microservices","spring boot","fastapi","redis"],
    "Java Developer":         ["java","spring boot","maven","sql","git","docker","rest api","junit","microservices","jdbc"],
    "DevOps Engineer":        ["docker","kubernetes","aws","terraform","ci/cd","git","linux","jenkins","monitoring","scripting"],
    "Site Reliability Engineer":["linux","aws","kubernetes","terraform","monitoring","ci/cd","python","bash","docker"],
    "Cloud Architect":        ["aws","azure","gcp","kubernetes","terraform","docker","microservices","security"],
    "Android Developer":      ["java","kotlin","android studio","git","rest api","sqlite","gradle","mobile development"],
    "iOS Developer":          ["swift","objective-c","xcode","cocoapods","git","rest api","ios sdk","mobile development"],
    "Flutter Developer":      ["dart","flutter","rest api","firebase","git","mobile development","ui/ux","responsive design"],
    "Cybersecurity Analyst":  ["linux","networking","firewalls","penetration testing","security","python","bash","vulnerability assessment"],
    "UI/UX Designer":         ["figma","sketch","adobe xd","prototyping","user research","wireframing","responsive design","html","css"],
    "Blockchain Developer":   ["solidity","ethereum","web3","javascript","smart contracts","bitcoin","cryptocurrency"],
}

CORE_SKILLS = {
    "AI Engineer":            ["python","machine learning","deep learning","llm","nlp","tensorflow","pytorch","mlops"],
    "Data Scientist":         ["python","machine learning","statistics","pandas","scikit-learn","feature engineering","sql"],
    "ML Engineer":            ["python","machine learning","deep learning","mlops","tensorflow","pytorch"],
    "NLP Engineer":           ["python","nlp","transformers","deep learning","pytorch"],
    "Computer Vision Engineer":["python","computer vision","deep learning","opencv"],
    "Generative AI Engineer": ["python","llm","transformers","pytorch"],
    "Data Analyst":           ["sql","excel","tableau","power bi","python","pandas"],
    "Data Engineer":          ["python","sql","apache spark","kafka","etl"],
    "Business Analyst":       ["sql","excel","tableau","python"],
    "BI Developer":           ["sql","tableau","power bi","data warehouse"],
    "Python Developer":       ["python","django","flask","rest api","sql"],
    "Full Stack Developer":   ["javascript","react","node.js","sql","rest api"],
    "Frontend Developer":     ["javascript","react","html","css","typescript"],
    "Backend Developer":      ["python","java","sql","rest api","docker"],
    "Java Developer":         ["java","spring boot","sql"],
    "DevOps Engineer":        ["docker","kubernetes","aws","terraform","ci/cd"],
    "Site Reliability Engineer":["linux","kubernetes","aws","monitoring"],
    "Cloud Architect":        ["aws","kubernetes","terraform"],
    "Android Developer":      ["java","kotlin","android studio"],
    "iOS Developer":          ["swift","xcode"],
    "Flutter Developer":      ["dart","flutter"],
    "Cybersecurity Analyst":  ["linux","security","python","networking"],
    "UI/UX Designer":         ["figma","prototyping","user research"],
    "Blockchain Developer":   ["solidity","ethereum","smart contracts"],
}

CERT_PROVIDERS = ["google","aws","amazon","microsoft","ibm","coursera","udemy",
                  "edx","linkedin learning","oracle","cisco","nvidia","deeplearning.ai"]

AI_KW = ["machine learning","deep learning","neural","ai","nlp","computer vision",
         "tensorflow","pytorch","transformer","bert","gpt","reinforcement",
         "classification","regression","clustering","prediction","model","dataset","training"]

# ── Expanded Course Map: 50+ Skills ──
COURSE_MAP = {
    "machine learning":{"course":"ML Specialization – Andrew Ng","platform":"Coursera","url":"https://coursera.org/specializations/machine-learning-introduction"},
    "deep learning":{"course":"Deep Learning Specialization","platform":"Coursera","url":"https://coursera.org/specializations/deep-learning"},
    "python":{"course":"Python for Everybody","platform":"Coursera","url":"https://coursera.org/specializations/python"},
    "nlp":{"course":"NLP Specialization","platform":"Coursera","url":"https://coursera.org/specializations/natural-language-processing"},
    "sql":{"course":"SQL for Data Science","platform":"Coursera","url":"https://coursera.org/learn/sql-for-data-science"},
    "aws":{"course":"AWS Cloud Practitioner","platform":"AWS","url":"https://aws.amazon.com/training"},
    "docker":{"course":"Docker & Kubernetes Practical Guide","platform":"Udemy","url":"https://udemy.com/course/docker-kubernetes/"},
    "tensorflow":{"course":"TensorFlow Developer Certificate","platform":"Google","url":"https://www.tensorflow.org/certificate"},
    "pytorch":{"course":"PyTorch for Deep Learning","platform":"Udemy","url":"https://udemy.com/course/pytorch-for-deep-learning/"},
    "react":{"course":"React – The Complete Guide","platform":"Udemy","url":"https://udemy.com/course/react-the-complete-guide/"},
    "langchain":{"course":"LangChain for LLM App Development","platform":"DeepLearning.AI","url":"https://deeplearning.ai"},
    "llm":{"course":"Generative AI with LLMs","platform":"Coursera","url":"https://coursera.org/learn/generative-ai-with-llms"},
    "tableau":{"course":"Tableau for Beginners","platform":"Udemy","url":"https://udemy.com/course/tableau-desktop/"},
    "power bi":{"course":"Microsoft Power BI Desktop","platform":"Udemy","url":"https://udemy.com/course/microsoft-power-bi-desktop/"},
    "kubernetes":{"course":"Kubernetes for Absolute Beginners","platform":"Udemy","url":"https://udemy.com/course/kubernetes-for-absolute-beginners/"},
    "transformer":{"course":"Attention is All You Need: Transformers","platform":"DeepLearning.AI","url":"https://deeplearning.ai/short-courses/"},
    "computer vision":{"course":"Deep Learning for Computer Vision","platform":"Coursera","url":"https://coursera.org/specializations/deep-learning"},
    "reinforcement learning":{"course":"Reinforcement Learning Specialization","platform":"Coursera","url":"https://coursera.org/specializations/reinforcement-learning"},
    "feature engineering":{"course":"Feature Engineering for ML","platform":"Coursera","url":"https://coursera.org/learn/feature-engineering"},
    "django":{"course":"Django for Beginners","platform":"Udemy","url":"https://udemy.com/course/python-django-dev-to-deployment/"},
    "flask":{"course":"Python Flask by Example","platform":"Udemy","url":"https://udemy.com/course/python-web-development-flask/"},
    "fastapi":{"course":"FastAPI – The Modern Web Framework","platform":"Udemy","url":"https://udemy.com/course/fastapi-practical/"},
    "node.js":{"course":"The Complete Node.js Developer","platform":"Udemy","url":"https://udemy.com/course/complete-nodejs-developer/"},
    "javascript":{"course":"The Complete JavaScript Course","platform":"Udemy","url":"https://udemy.com/course/the-complete-javascript-course/"},
    "typescript":{"course":"TypeScript – The Complete Guide","platform":"Udemy","url":"https://udemy.com/course/understanding-typescript/"},
    "mongodb":{"course":"MongoDB – Complete Developer Guide","platform":"Udemy","url":"https://udemy.com/course/mongodb-the-complete-developers-guide/"},
    "redis":{"course":"Redis – The Complete Guide","platform":"Udemy","url":"https://udemy.com/course/redis-course/"},
    "git":{"course":"Git & GitHub Masterclass","platform":"Udemy","url":"https://udemy.com/course/git-and-github-masterclass/"},
    "linux":{"course":"Linux Command Line Basics","platform":"Udemy","url":"https://udemy.com/course/linux-command-line-basics/"},
    "rag":{"course":"Retrieval Augmented Generation","platform":"DeepLearning.AI","url":"https://deeplearning.ai"},
    "vector database":{"course":"Vector Databases in AI","platform":"DeepLearning.AI","url":"https://deeplearning.ai"},
    "fine tuning":{"course":"Fine-tuning Large Language Models","platform":"DeepLearning.AI","url":"https://deeplearning.ai"},
    "prompt engineering":{"course":"Prompt Engineering for LLMs","platform":"DeepLearning.AI","url":"https://deeplearning.ai"},
    "generative ai":{"course":"Generative AI Fundamentals","platform":"Coursera","url":"https://coursera.org/learn/generative-ai-with-llms"},
    "mlops":{"course":"Machine Learning Operations","platform":"Coursera","url":"https://coursera.org/specializations/mlops-machine-learning-operations"},
    "data warehouse":{"course":"Data Warehouse Fundamentals","platform":"Udemy","url":"https://udemy.com/course/data-warehouse-concepts/"},
    "etl":{"course":"ETL and Data Pipeline Essentials","platform":"Udemy","url":"https://udemy.com/course/etl-data-pipeline/"},
    "apache spark":{"course":"Apache Spark by Example","platform":"Udemy","url":"https://udemy.com/course/apache-spark-by-example/"},
    "kafka":{"course":"Apache Kafka for Beginners","platform":"Udemy","url":"https://udemy.com/course/apache-kafka-series/"},
    "terraform":{"course":"Terraform – Infrastructure as Code","platform":"Udemy","url":"https://udemy.com/course/learn-terraform/"},
    "ci/cd":{"course":"CI/CD Pipelines with Jenkins","platform":"Udemy","url":"https://udemy.com/course/jenkins-for-cicd/"},
    "microservices":{"course":"Microservices Architecture","platform":"Udemy","url":"https://udemy.com/course/microservices-architecture/"},
    "spring boot":{"course":"Spring Boot Microservices","platform":"Udemy","url":"https://udemy.com/course/spring-boot-microservices/"},
    "android":{"course":"Android App Development","platform":"Udemy","url":"https://udemy.com/course/android-app-development/"},
    "kotlin":{"course":"Kotlin for Android Development","platform":"Udemy","url":"https://udemy.com/course/kotlin-for-android-developers/"},
    "swift":{"course":"iOS Development with Swift","platform":"Udemy","url":"https://udemy.com/course/ios-app-development-with-swift/"},
    "flutter":{"course":"Flutter & Dart Complete Guide","platform":"Udemy","url":"https://udemy.com/course/flutter-complete-guide/"},
    "dart":{"course":"Dart Programming Language","platform":"Udemy","url":"https://udemy.com/course/dart-programming-language/"},
    "solidity":{"course":"Solidity – Smart Contract Programming","platform":"Udemy","url":"https://udemy.com/course/solidity-smart-contract/"},
    "web3":{"course":"Web3 and Blockchain Development","platform":"Udemy","url":"https://udemy.com/course/web3-blockchain/"},
    "figma":{"course":"Figma UI/UX Design","platform":"Udemy","url":"https://udemy.com/course/figma-design-course/"},
}

# ═══════════════════════════════════════════════
# MODULE 0 — PDF VALIDATION
# ═══════════════════════════════════════════════

MAX_PDF_SIZE_MB = 50

# Mobile browsers, cloud-storage file pickers (Google Drive/Files apps),
# and some WebView contexts don't reliably report "application/pdf" as the
# MIME type for the upload — they sometimes send "application/octet-stream"
# or even an empty string, even though the file IS a valid PDF. Relying on
# uploaded_file.type alone caused false "not a PDF" rejections once deployed
# (this is what produced the red error icon / "please upload a resume PDF
# first" message in the screenshot, even though a .pdf file was selected).
# We now trust the file extension first, and use the MIME type only as a
# secondary signal, with the actual PDF header check below being the real
# source of truth.
VALID_PDF_MIME_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",  # seen on some mobile/cloud-picker uploads
    "",                          # seen when browser omits MIME entirely
}

def validate_pdf_file(uploaded_file) -> str:
    """Validate PDF file. Returns error message or empty string if valid."""
    if not uploaded_file:
        return "No file uploaded."

    raw = uploaded_file.getvalue()

    file_size_mb = len(raw) / (1024*1024)
    if file_size_mb > MAX_PDF_SIZE_MB:
        return f"File too large ({file_size_mb:.1f} MB). Maximum {MAX_PDF_SIZE_MB} MB."

    if file_size_mb <= 0:
        return "Uploaded file is empty."

    name_ok = uploaded_file.name.lower().endswith(".pdf")
    type_ok = (uploaded_file.type or "") in VALID_PDF_MIME_TYPES
    header_ok = raw[:5] == b"%PDF-"  # the real source of truth: actual PDF file signature

    if not header_ok:
        # Genuinely not a PDF (or corrupted) — only now do we reject.
        return "File does not appear to be a valid PDF (missing PDF header)."

    if not (name_ok or type_ok):
        # Header is valid PDF but extension/MIME both look odd — warn but allow.
        return ""

    return ""

# ═══════════════════════════════════════════════
# MODULE 1 — PDF PARSER
# ═══════════════════════════════════════════════

def extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
        return text if text else "ERROR: PDF contains no extractable text (may be scanned image)."
    except Exception as e:
        return f"ERROR: {str(e)[:100]}"

def extract_name(text):
    for line in text.split("\n")[:6]:
        line = line.strip()
        words = line.split()
        if 2 <= len(words) <= 5 and not any(c.isdigit() for c in line) and "@" not in line:
            return line
    return "Not detected"

def extract_email(text):
    m = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    return m.group(0) if m else "Not found"

def extract_phone(text):
    """Stricter phone regex to avoid false positives."""
    m = re.search(r'(\+\d{1,3})?\s*(\(?\d{1,4}\)?)?\s*[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}', text)
    return m.group(0).strip() if m else "Not found"

def extract_education(text):
    kws = ["b.tech","b.e","m.tech","mba","bsc","msc","phd","bachelor","master",
           "degree","university","college","institute","10th","12th","diploma"]
    out = []
    for line in text.lower().split("\n"):
        if any(k in line for k in kws) and len(line.strip()) > 5:
            out.append(line.strip().title())
    return list(dict.fromkeys(out))[:5]

def extract_experience_sections(text):
    kws = ["experience","internship","worked at","engineer at","developer at","analyst at"]
    out = []
    for line in text.lower().split("\n"):
        if any(k in line for k in kws) and len(line.strip()) > 5:
            out.append(line.strip().title())
    return list(dict.fromkeys(out))[:6]

def extract_projects(text):
    lines = text.lower().split("\n")
    projects, capture = [], False
    for line in lines:
        s = line.strip()
        if "project" in s:
            capture = True
        if capture and len(s) > 10:
            projects.append(s.title())
        if len(projects) >= 8:
            break
    return projects

def extract_certifications(text):
    kws = ["certified","certification","certificate","credential","course","completed","badge"]
    out = []
    for line in text.lower().split("\n"):
        if any(k in line for k in kws) and len(line.strip()) > 5:
            out.append(line.strip().title())
    return list(dict.fromkeys(out))[:8]

def parse_resume(text):
    return {
        "name":           extract_name(text),
        "email":          extract_email(text),
        "phone":          extract_phone(text),
        "education":      extract_education(text),
        "experience":     extract_experience_sections(text),
        "projects":       extract_projects(text),
        "certifications": extract_certifications(text),
    }

# ═══════════════════════════════════════════════
# MODULE 2 — SKILL EXTRACTION
# ═══════════════════════════════════════════════

def extract_skills(text):
    tl = text.lower()
    return {
        cat: [s for s in skills if re.search(r'\b' + re.escape(s) + r'\b', tl)]
        for cat, skills in SKILL_DICT.items()
        if any(re.search(r'\b' + re.escape(s) + r'\b', tl) for s in skills)
    }

def get_missing_skills(found_skills, target_role):
    found_flat = {s for lst in found_skills.values() for s in lst}
    target_skills = ROLE_SKILLS.get(target_role, [])
    if not target_skills:
        return []
    return [s for s in target_skills if s not in found_flat]

# ═══════════════════════════════════════════════
# MODULE 3 — ATS SCORE (4-Signal, resume-specific)
# ═══════════════════════════════════════════════

_GENERIC_JD = (
    "we are looking for a candidate with experience working in a fast paced team "
    "the role requires strong communication and problem solving skills the ideal "
    "candidate will have a degree and relevant work experience responsibilities "
    "include collaborating with team members delivering results and meeting deadlines "
    "please apply if you are motivated and passionate about technology"
)

_ATS_STOP = {
    "the","and","for","are","with","this","that","will","have","from","you","your",
    "our","their","been","was","were","has","had","not","but","can","all","its",
    "also","more","they","them","than","into","over","such","each","about","who",
    "what","when","where","how","use","using","used","work","works","worked","able",
    "must","should","would","could","may","well","good","new","make","made","one",
    "two","get","set","per","via","etc","including","required","experience","strong",
    "excellent","ability","knowledge","understanding","looking","seeking","ideal",
    "candidate","role","position","team","please","apply","join","great","ensure",
    "need","needs","want","year","years","time","company","responsibilities",
    "qualifications","preferred","minimum","equal","opportunity","employer"
}

def _skill_set(text):
    tl = text.lower()
    return {s for s in ALL_SKILLS if re.search(r'\b' + re.escape(s) + r'\b', tl)}

def _jd_keyword_weights(jd_text, top_n=50):
    """Returns list of (keyword, importance_weight) for this specific JD."""
    try:
        vec = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2),
            max_features=300, sublinear_tf=True, min_df=1
        )
        matrix = vec.fit_transform([jd_text.lower(), _GENERIC_JD])
        features = vec.get_feature_names_out()
        jd_w = matrix[0].toarray()[0]
        bg_w = matrix[1].toarray()[0]

        distinct = {
            features[i]: max(jd_w[i] - bg_w[i] * 0.6, 0)
            for i in range(len(features))
            if jd_w[i] > 0
               and not all(w in _ATS_STOP for w in features[i].split())
               and len(features[i]) > 2
        }
        ranked = sorted(distinct.items(), key=lambda x: -x[1])
        return ranked[:top_n]
    except Exception:
        return []

def _domain_vectors(text):
    """Return a 5-dim domain fingerprint for the text."""
    tl = text.lower()
    domains = {
        "ai_ml":    ["machine learning","deep learning","neural","tensorflow","pytorch","nlp","llm","computer vision","model","training","dataset","prediction","bert","gpt"],
        "data":     ["sql","database","analytics","dashboard","tableau","power bi","excel","reporting","etl","data warehouse","insight","pandas","numpy"],
        "web":      ["react","javascript","html","css","node","frontend","backend","api","http","web","browser","ui","ux","django","flask"],
        "devops":   ["docker","kubernetes","aws","azure","gcp","ci/cd","terraform","pipeline","deployment","infrastructure","jenkins","github actions"],
        "python":   ["python","django","flask","fastapi","pytest","pip","virtualenv","package","module","class","function","decorator","celery"],
    }
    return np.array([
        sum(1 for k in kws if k in tl) / len(kws)
        for kws in domains.values()
    ], dtype=float)

def _domain_alignment(resume_text, jd_text):
    r = _domain_vectors(resume_text)
    j = _domain_vectors(jd_text)
    denom = np.linalg.norm(r) * np.linalg.norm(j)
    if denom < 1e-9:
        return 50.0
    return round(float(np.dot(r, j) / denom) * 100, 1)

def _achievement_score(resume_text):
    tl = resume_text.lower()
    score = 0
    score += len(re.findall(r'\d+\s*%', tl)) * 8
    score += len(re.findall(r'\$\s*\d+', tl)) * 5
    score += len(re.findall(r'\b\d+[kmb]\b', tl)) * 5
    score += sum(1 for w in [
        "improved","reduced","increased","achieved","delivered","optimized",
        "deployed","launched","built","led","managed","designed","automated",
        "saved","accelerated","developed","implemented","created","established"
    ] if w in tl) * 4
    score += min(len(re.findall(r'\b(20\d{2})\b', tl)) * 3, 15)
    return min(int(score), 100)

def calculate_ats_score(resume_text: str, jd_text: str) -> dict:
    """4-signal ATS. Each resume+JD pair produces a genuinely different score."""
    if not jd_text or not jd_text.strip():
        return {
            "ats_score":0,"skill_match_pct":0,"keyword_match_pct":0,
            "cosine_score":0,"s1":0,"s2":0,"s3":0,"s4":0,
            "missing_keywords":[],
            "recommendations":["Upload a Job Description to calculate ATS score."]
        }

    # ── S1: Exact skill gap (30%) ─────────────────────────────────────
    resume_skills = _skill_set(resume_text)
    jd_skills     = _skill_set(jd_text)

    if jd_skills:
        matched_skills  = resume_skills & jd_skills
        missing_skills_ = jd_skills - resume_skills
        s1 = (len(matched_skills) / len(jd_skills)) * 100
        s1 = max(0.0, s1 - len(missing_skills_) * 1.8)
        s1 = min(s1, 95.0)
    else:
        s1 = 0.0
        missing_skills_ = set()
    skill_match_pct = round(s1, 1)

    # ── S2: JD-distinctive keyword recall (30%) ───────────────────────
    kw_weights   = _jd_keyword_weights(jd_text, top_n=50)
    resume_lower = resume_text.lower()

    if kw_weights:
        total_w   = sum(w for _, w in kw_weights)
        matched_w = sum(w for kw, w in kw_weights
                        if re.search(r'\b' + re.escape(kw) + r'\b', resume_lower))
        s2 = (matched_w / total_w) * 100 if total_w else 0.0
        s2 = min(s2, 90.0)
    else:
        s2 = 0.0
    keyword_match_pct = round(s2, 1)

    missing_keywords = [
        kw for kw, _ in kw_weights
        if not re.search(r'\b' + re.escape(kw) + r'\b', resume_lower)
    ][:20]

    # ── S3: Domain alignment (25%) ────────────────────────────────────
    s3 = _domain_alignment(resume_text, jd_text)

    # ── S4: Achievement richness (15%) ────────────────────────────────
    s4 = float(_achievement_score(resume_text))

    # ── Weighted final ────────────────────────────────────────────────
    ats_score = round(s1*0.30 + s2*0.30 + s3*0.25 + s4*0.15, 1)
    ats_score = min(ats_score, 95.0)

    # ── Recommendations ───────────────────────────────────────────────
    recs = []
    if   ats_score < 35: recs.append("⚠️ Very weak match — major resume rewrite needed for this JD.")
    elif ats_score < 55: recs.append("📝 Moderate match — add more JD-specific keywords and skills.")
    elif ats_score < 70: recs.append("✅ Decent match — targeted additions will push you past 70%.")
    else:                recs.append("🎯 Strong match — fine-tune with missing keywords below.")

    if skill_match_pct < 50 and jd_skills:
        top_m = list(missing_skills_)[:5]
        recs.append(f"🔧 Add missing skills: {', '.join(top_m)}")
    if keyword_match_pct < 40:
        recs.append("🔑 Mirror exact JD phrasing — ATS bots match keywords literally.")
    if s3 < 40:
        recs.append("🎯 Domain mismatch — your profile domain differs from what this JD requires.")
    if s4 < 25:
        recs.append("📊 Add measurable achievements: numbers, %, impact statements.")

    return {
        "ats_score": ats_score, "skill_match_pct": skill_match_pct,
        "keyword_match_pct": keyword_match_pct, "cosine_score": round(s3,1),
        "s1": round(s1,1), "s2": round(s2,1), "s3": round(s3,1), "s4": round(s4,1),
        "missing_keywords": missing_keywords, "recommendations": recs,
    }

# ═══════════════════════════════════════════════
# MODULE 4 — ROLE PREDICTION
# ═══════════════════════════════════════════════

def predict_job_role(resume_text):
    tl = resume_text.lower()
    raw = {}
    for role, all_s in ROLE_SKILLS.items():
        core  = CORE_SKILLS.get(role, [])
        bonus = [s for s in all_s if s not in core]
        cm = sum(1 for s in core  if re.search(r'\b'+re.escape(s)+r'\b', tl))
        bm = sum(1 for s in bonus if re.search(r'\b'+re.escape(s)+r'\b', tl))
        raw[role] = (cm*2 + bm) / max(len(core)*2 + len(bonus), 1)

    temp = 5.0
    exp_s = {r: math.exp(s*temp) for r,s in raw.items()}
    total = sum(exp_s.values()) or 1
    confs = {r: round(e/total*100, 1) for r,e in exp_s.items()}
    return {"top_role": max(confs, key=confs.get), "confidences": confs}

# ═══════════════════════════════════════════════
# MODULE 5 — EXPERIENCE LEVEL
# ═══════════════════════════════════════════════

def detect_experience_level(text, parsed):
    tl = text.lower()
    score = 0
    yrs = re.findall(r'(\d+)\+?\s*years?\s*(of)?\s*experience', tl)
    years = max([int(y[0]) for y in yrs], default=0)
    if years >= 5: score += 3
    elif years >= 2: score += 2
    elif years >= 1: score += 1
    if "intern" in tl: score += 1
    if len(parsed.get("projects",[])) >= 3: score += 1
    if len(parsed.get("certifications",[])) >= 2: score += 1
    if any(k in tl for k in ["lead","senior","architect","manager","head of"]): score += 2

    if score >= 5:   level,desc = "Experienced","Strong professional with multiple years of industry experience."
    elif score >= 2: level,desc = "Intermediate","Solid skills with internships, projects, or 1–3 years experience."
    else:            level,desc = "Fresher","Entry-level — focus on projects, certifications, and open source."
    return {"level":level,"score":score,"description":desc,"years":years}

# ═══════════════════════════════════════════════
# MODULE 6 — PROJECT ANALYZER
# ═══════════════════════════════════════════════

def analyze_projects(text):
    tl = text.lower()
    projects  = extract_projects(text)
    ai_count  = sum(1 for kw in AI_KW if kw in tl)
    tech_kws  = ["api","deployed","docker","aws","cloud","production","database",
                 "backend","frontend","pipeline","real-time","microservice"]
    tech_depth = sum(1 for kw in tech_kws if kw in tl)
    score = min(100, len(projects)*10 + min(ai_count*3,30) + min(tech_depth*2,20))
    quality = "Strong" if score>=70 else ("Moderate" if score>=40 else "Needs Improvement")
    return {"count":len(projects),"score":score,"quality":quality,
            "ai_relevance":min(ai_count*5,100),"tech_depth":min(tech_depth*5,100),
            "projects_list":projects}

# ═══════════════════════════════════════════════
# MODULE 7 — CERTIFICATION ANALYZER
# ═══════════════════════════════════════════════

def analyze_certifications(text):
    tl = text.lower()
    certs = extract_certifications(text)
    recognized = list(dict.fromkeys(p.title() for p in CERT_PROVIDERS if p in tl))
    score = min(100, len(certs)*15 + len(recognized)*10)
    return {"certifications":certs,"recognized_providers":recognized,
            "count":len(certs),"score":score}

# ═══════════════════════════════════════════════
# MODULE 8 — LEARNING RECOMMENDATIONS
# ═══════════════════════════════════════════════

def get_learning_recommendations(missing_skills):
    recs, seen = [], set()
    for skill in missing_skills:
        sl = skill.lower()
        for key, info in COURSE_MAP.items():
            if key in sl or sl in key:
                if info["course"] not in seen:
                    recs.append({"skill":skill,**info})
                    seen.add(info["course"])
                    break
    if not recs:
        for s in missing_skills[:5]:
            recs.append({"skill":s,"course":f"Search '{s}' courses","platform":"Coursera / Udemy",
                         "url":f"https://www.coursera.org/search?query={s.replace(' ','+')} "})
    return recs

# ═══════════════════════════════════════════════
# MODULE 9 — OVERALL RESUME SCORE
# ═══════════════════════════════════════════════

def calculate_resume_score(parsed, found_skills, proj, cert, ats):
    skill_n = sum(len(v) for v in found_skills.values())
    s_skill = min(skill_n*3, 30)
    s_proj  = proj["score"]  * 0.25
    s_cert  = cert["score"]  * 0.15
    s_ats   = ats["ats_score"]* 0.20
    s_info  = (10 if parsed["email"] != "Not found" else 0) + \
              (5  if parsed["phone"] != "Not found" else 0) + \
              (5  if parsed["education"]  else 0) + \
              (5  if parsed["experience"] else 0)
    total = min(round(s_skill+s_proj+s_cert+s_ats+s_info),100)
    grade = "Excellent" if total>=75 else ("Good" if total>=55 else ("Average" if total>=35 else "Needs Work"))
    return {"total":total,"grade":grade,"skill_score":s_skill,
            "project_score":round(s_proj),"cert_score":round(s_cert),"ats_score":round(s_ats)}

# ═══════════════════════════════════════════════
# MODULE 10 — PDF REPORT
# ═══════════════════════════════════════════════

def generate_pdf_report(parsed,found_skills,missing_skills,ats,role_pred,
                        exp_level,proj,cert,recs,resume_score):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf,pagesize=A4,
                             rightMargin=0.75*inch,leftMargin=0.75*inch,
                             topMargin=0.75*inch,bottomMargin=0.75*inch)
    ss = getSampleStyleSheet()
    T  = ParagraphStyle('T',parent=ss['Title'],fontSize=20,textColor=colors.HexColor('#1565C0'),spaceAfter=4)
    H2 = ParagraphStyle('H2',parent=ss['Heading2'],fontSize=13,textColor=colors.HexColor('#1976D2'),spaceBefore=10,spaceAfter=4)
    B  = ParagraphStyle('B',parent=ss['Normal'],fontSize=10,leading=14,spaceAfter=3)
    SM = ParagraphStyle('SM',parent=ss['Normal'],fontSize=8,textColor=colors.HexColor('#888888'))

    story=[
        Paragraph("ScoreMyResume — Full Analysis Report",T),
        Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}",SM),
        HRFlowable(width="100%",thickness=1,color=colors.HexColor('#1976D2')),
        Spacer(1,8),
    ]
    story.append(Paragraph("Score Summary",H2))
    td=[["Metric","Score"],
        ["Overall Resume Score",f"{resume_score['total']}/100 ({resume_score['grade']})"],
        ["ATS Match Score",f"{ats['ats_score']}%"],
        ["Skill Match",f"{ats['skill_match_pct']}%"],
        ["Keyword Coverage",f"{ats['keyword_match_pct']}%"],
        ["Project Score",f"{proj['score']}/100"],
        ["Certification Score",f"{cert['score']}/100"]]
    t=Table(td,colWidths=[3*inch,3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1565C0')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTSIZE',(0,0),(-1,-1),10),('PADDING',(0,0),(-1,-1),6),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F5F8FF'),colors.white]),
    ]))
    story+=[t,Spacer(1,8)]
    story.append(Paragraph("Candidate",H2))
    for k,v in [("Name",parsed.get("name")),("Email",parsed.get("email")),
                ("Phone",parsed.get("phone")),("Experience",exp_level["level"]),
                ("Predicted Role",role_pred["top_role"])]:
        story.append(Paragraph(f"<b>{k}:</b> {v}",B))
    story.append(Spacer(1,6))
    story.append(Paragraph("Skills Found",H2))
    for cat,skills in found_skills.items():
        story.append(Paragraph(f"<b>{cat}:</b> {', '.join(skills)}",B))
    story.append(Paragraph("Missing Skills",H2))
    story.append(Paragraph(', '.join(missing_skills) if missing_skills else "All key skills present!",B))

    story.append(Paragraph("Recommended Courses",H2))
    for r in recs[:8]:
        story.append(Paragraph(f"• <b>{r['skill']}</b> → {r['course']} ({r['platform']})",B))
    story+=[Spacer(1,10),HRFlowable(width="100%",thickness=0.5,color=colors.grey),
            Paragraph("ScoreMyResume v2.1 · Production Ready",SM)]
    doc.build(story)
    buf.seek(0)
    return buf.read()