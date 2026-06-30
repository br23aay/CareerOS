"""
core/master_cv.py — your real CV content, structured so the Resume Factory can
tailor a fresh ATS-safe resume per job WITHOUT inventing anything.

Everything here is drawn verbatim from your master CV and portfolio. The
factory only ever REORDERS, SELECTS, and RE-EMPHASISES these real facts to
match a job description. It never adds a skill or claim that isn't here.
"""

CONTACT = {
    "name": "BHARADWAJ RACHURI",
    "location": "Hatfield, United Kingdom",
    "phone": "07586 362964",
    "email": "bharadwaj.r.career@gmail.com",
    "linkedin": "linkedin.com/in/bharadwaj-rachuri",
    "github": "github.com/br23aay",
    "portfolio": "br23aay.github.io",
}

# Base summary; the factory swaps the lead clause to match the role family.
SUMMARY_BASE = (
    "Graduate AI Engineer with an MSc in Artificial Intelligence and Robotics "
    "(Commendation, University of Hertfordshire, 2025) and peer-reviewed "
    "research in reinforcement learning (IJRES, Impact Factor 7.52). "
    "Right to work in the UK — Post-Study Work visa, no sponsorship required. "
    "Available immediately."
)

# Skill groups exactly as on your CV. The factory orders these by relevance
# to the job description and drops groups the JD doesn't touch.
SKILL_GROUPS = {
    "LLM & NLP": ["Large Language Models", "Fine-tuning (LLaMA, Mistral, GPT)",
                  "RAG", "Prompt Engineering", "Transformers",
                  "Attention Mechanisms", "Embeddings", "Tokenization"],
    "ML Frameworks": ["PyTorch", "TensorFlow", "Stable-Baselines3",
                      "Scikit-learn", "Keras"],
    "MLOps & Tools": ["MLflow", "Azure AI Foundry", "Prompt Flow",
                      "Model Evaluation", "Benchmarking", "Dataset Pipelines"],
    "Cloud & AI Platforms": ["Microsoft Azure (AI, Language, Vision, Speech)",
                             "Microsoft Fabric", "Azure AI Foundry SDK"],
    "Programming": ["Python (proficient)", "R", "C#", "Java"],
    "Reinforcement Learning & Robotics": ["Reinforcement Learning (PPO)",
                                          "MuJoCo", "Robotics Simulation",
                                          "Shadow Hand (24-DoF)"],
    "Vector & Data": ["RAG pipelines", "Data preprocessing",
                      "Feature engineering", "NumPy", "Pandas"],
    "Responsible AI": ["Azure Responsible AI framework", "Safety checks",
                       "Guardrails", "Compliance"],
    "Other": ["Git", "Jupyter", "REST APIs", "FastAPI"],
}

EDUCATION = [
    {"title": "MSc Artificial Intelligence and Robotics — Commendation",
     "place": "University of Hertfordshire, UK", "dates": "Jan 2024 – Jul 2025",
     "points": [
        "Published researcher — IJRES Vol. 13, Issue 6, pp. 164–183 | Impact Factor 7.52",
        "Key modules: Machine Learning, Neural Networks, Artificial Life with Robotics, Responsible Technology",
        "MSc Project: Trained Shadow Hand (24-DoF) using PPO in MuJoCo — achieved 175° pen rotation, >90% sensor accuracy"]},
    {"title": "B.Tech Mechanical Engineering",
     "place": "Guntur Engineering College, India", "dates": "Aug 2017 – Sep 2021",
     "points": [
        "Final project: Static Analysis of Spur Gear using FEA (Fusion 360 + ANSYS Workbench)",
        "Siemens certified: Milling NC Programming and Milling Operating & Machining (2019)"]},
]

EXPERIENCE = [
    {"title": "Machine Learning & AI Engineer", "place": "Swayam Ltd, London",
     "dates": "May 2025 – Jun 2026",
     # All points below are taken directly from the signed Swayam reference
     # letter (Nikhil Bussa, Manager). Tailored per job by the factory.
     "tags": ["python", "tensorflow", "pytorch", "llm", "slm", "vision",
              "computer vision", "rag", "flask", "rest api", "azure", "aws",
              "ci/cd", "git", "sql", "deep learning", "machine learning",
              "reinforcement learning", "ppo", "mujoco"],
     "points": [
        "Designed, developed and evaluated machine learning and deep learning models using Python, TensorFlow and PyTorch for client-facing projects",
        "Built AI systems incorporating Large Language Models (LLMs), Small Language Models (SLMs) and Vision Models across multiple client sectors",
        "Developed and deployed RESTful APIs using Flask to serve model outputs in production",
        "Worked with reinforcement learning pipelines (PPO), MuJoCo simulation and sim-to-real transfer workflows",
        "Used Microsoft Azure AI and AWS, and maintained CI/CD pipelines with Git and GitHub",
        "Built SQL-based data pipelines for model training and evaluation"]},
    {"title": "Independent AI/ML Engineer", "place": "Self-employed, Freelance",
     "dates": "May 2025 – Present",
     "tags": ["python", "scikit-learn", "llm", "rag", "azure", "fastapi"],
     "points": [
        "Built and trained ML models for classification, prediction and reasoning tasks using Python",
        "Designed LLM evaluation workflows including prompt refinement and structured output analysis",
        "Developed RAG-based pipelines and prompt-driven applications using Azure AI Foundry",
        "Completed 49 Microsoft Azure AI certifications covering LLMs, RAG, fine-tuning, NLP, Computer Vision and responsible AI"]},
]

# Each project is tagged with the skills it evidences, so the factory can pick
# the 2-3 projects most relevant to a given job.
PROJECTS = [
    {"title": "Dexterous In-Hand Manipulation (Shadow Hand)", "dates": "2024–2025",
     "tags": ["reinforcement learning", "ppo", "mujoco", "robotics", "pytorch",
              "research", "python"],
     "points": [
        "Built a custom MuJoCo environment to rotate a pen 180° with a 24-DoF Shadow Hand",
        "Achieved 175° rotation, >90% touch sensor accuracy, reproduced across 3 independent seeds",
        "Published in IJRES Vol. 13, Issue 6, pp. 164–183 | Impact Factor 7.52",
        "GitHub: github.com/br23aay/shadowhand-dexterity-ppo"]},
    {"title": "Azure AI LLM Workflow Development", "dates": "2024–2025",
     "tags": ["llm", "rag", "azure", "prompt engineering", "responsible ai",
              "fine-tuning", "nlp"],
     "points": [
        "Built RAG solutions using Azure AI Foundry — retrieval pipelines, context management, grounding outputs",
        "Fine-tuned language models and built prompt flow pipelines for structured output generation",
        "Implemented responsible AI evaluation frameworks and safety guardrails",
        "Developed SDK-based AI applications with model evaluation and benchmarking (100+ outputs)"]},
    {"title": "Autonomous Robotic Navigation — Unity", "dates": "2024",
     "tags": ["robotics", "c#", "computer vision", "simulation"],
     "points": [
        "Built sensor-driven autonomous car in Unity using C# — achieved 100/100 score",
        "Implemented 7-sensor raycast array, lane-keeping logic and real-time obstacle avoidance",
        "Demo: youtube.com/watch?v=2VZP29PA1Jk"]},
]

CERTIFICATIONS = [
    "Azure AI Foundry: RAG solutions, model fine-tuning, prompt flow, SDK app development, responsible AI",
    "Microsoft Fabric: Data Science, MLflow tracking, batch inference, data wrangling, end-to-end analytics",
    "Azure AI — NLP & Speech: conversational models, Q&A systems, NER, speech/text translation",
    "Azure AI — Computer Vision: image/video analysis, object & face detection, OCR",
    "AI Foundations: AI/ML/GenAI fundamentals, AI agents, information extraction",
]

PUBLICATION = ("Rachuri, B. & Faria, D.R. (2025). Reinforcement Learning for "
               "Robot Dexterous In-Hand Manipulation of Objects (Shadow Hand). "
               "IJRES, Vol. 13, Issue 6, pp. 164–183. ISSN: 2320-9364. "
               "Impact Factor: 7.52.")

ADDITIONAL = [
    "Right to work in the UK — Post-Study Work (PSW) visa, 2 years, no sponsorship required",
    "Available for immediate start",
    "Willing to travel within UK for client engagements",
]

# Role-family lead clauses for the summary, chosen by JD keywords.
LEAD_CLAUSES = {
    "llm": "AI/ML Engineer specialising in LLM workflows, RAG pipelines and prompt engineering",
    "robotics": "AI & Robotics Engineer with published reinforcement-learning research and hands-on MuJoCo experience",
    "data": "Machine Learning Engineer with strong Python, data-pipeline and model-evaluation experience",
    "vision": "AI Engineer with computer-vision exposure across Azure Vision and simulation projects",
    "research": "AI Research Engineer with a peer-reviewed reinforcement-learning publication",
    "software": "Graduate Software Engineer with strong Python and end-to-end ML delivery experience",
}
