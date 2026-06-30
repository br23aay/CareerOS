"""
core/profile.py — your profile as structured data (single source of truth).

Every department scores/drafts against this. Edit here when anything changes.
"""

NAME = "Bharadwaj Rachuri"
EMAIL = "bharadwaj.r.career@gmail.com"
PHONE = "07586 362964"
LOCATION = "Hatfield, Hertfordshire"
LINKEDIN = "linkedin.com/in/bharadwaj-rachuri"
GITHUB = "github.com/br23aay"
PORTFOLIO = "br23aay.github.io"
VISA = "Graduate Visa (PSW) — full right to work until 29 September 2027"
NEEDS_SPONSORSHIP = False

# --- Salary (CHECK THESE — you are between roles; Swayam ended Jun 2026) ---
# Blueprint hard-coded £34,000 current salary. Set realistically before the
# Salary department anchors negotiations on it.
CURRENT_SALARY = None          # between roles
MINIMUM_SALARY = 28_000
TARGET_SALARY = 40_000
SALARY_FLOOR = 25_000          # never apply below this
SALARY_TARGET_LOW = 28_000
SALARY_TARGET_HIGH = 35_000

# --- Skills (weighted) -----------------------------------------------------
SKILLS = {
    "python": 3, "pytorch": 3, "reinforcement learning": 3, "ppo": 3,
    "mujoco": 3, "stable-baselines3": 3, "robotics": 3, "shadow hand": 3,
    "rag": 2, "llm": 2, "azure": 2, "fastapi": 2, "scikit-learn": 2,
    "machine learning": 2, "deep learning": 2, "computer vision": 2,
    "nlp": 2, "docker": 2, "transformers": 2, "tensorflow": 2,
    "sql": 1, "java": 1, "git": 1, "rest api": 1, "pandas": 1, "numpy": 1,
    "mlflow": 1, "selenium": 1, "c#": 1, "linux": 1, "chromadb": 1,
}
DEVELOPING = ["langchain", "langgraph", "agentic", "kubernetes", "spark",
              "terraform", "ros", "c++", "gcp"]

# --- Reject rules (from MASTER "REJECT IMMEDIATELY") -----------------------
REJECT_PHRASES = [
    "sc clearance", "dv clearance", "security clearance", "nsv", "nsc",
    "developed vetting", "sole british national",
    "phd required", "currently enrolled phd", "phd candidate",
    "native german", "fluent german", "fluent french", "native french",
    "german speaking", "french speaking",
]
SENIOR_PHRASES = ["senior ", "lead ", "principal ", "head of ",
                  "director", "manager", "staff engineer", "vp "]
MIN_YEARS_REJECT = 3
# Great Britain only (England, Scotland, Wales) — Northern Ireland excluded
# per user preference, and Republic of Ireland excluded as a separate country.
# Note: "ireland" also matches inside "northern ireland", but the explicit NI
# towns below catch Belfast-area listings that omit the word "ireland".
NON_UK_MARKERS = ["ireland", "dublin", "germany", "berlin", "france", "paris",
                  "spain", "netherlands", "amsterdam", "usa", "united states",
                  "new york", "remote (eu)", "remote eu", "poland", "india",
                  "northern ireland", "belfast", "derry", "londonderry",
                  "lisburn", "newry", "armagh", "antrim", "ballymena",
                  "bt postcode", "co. down", "co. antrim", "co. armagh",
                  "co. tyrone", "co. fermanagh", "co. londonderry"]

# --- Flag rules (from MASTER "FLAG IMMEDIATELY") ---------------------------
FLAG_COMPANIES = ["shadow robot", "anthropic", "deepmind", "faculty",
                  "wayve", "reply", "humanoid", "graphcore"]
FLAG_KEYWORDS = ["humanoid", "robotics", "remote uk", "fully remote"]

# --- CV variant selection --------------------------------------------------
CV_LIBRARY = {
    "anthropic": "Anthropic_v2", "ai safety": "Anthropic_v2",
    "shadow robot": "ShadowRobot_v2", "robotics software": "ShadowRobot_v2",
    "deep learning": "DeepLearning", "computer vision": "DeepLearning",
    "neural network": "DeepLearning", "cloud": "TechnicalEngineer",
    "saas": "TechnicalEngineer", "consultant": "TechnicalEngineer",
    "iot": "TechnicalEngineer",
}
CV_DEFAULT = "SailReply"


def recommend_cv(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for keyword, cv in CV_LIBRARY.items():
        if keyword in text:
            return cv
    return CV_DEFAULT
