"""
frontend/app.py — CareerOS command centre.

Design: a dark "mission control" theme — focused, alive, purposeful. Animated
gradient header, glowing accents, smooth card reveals. Left-rail navigation.
Every page wired to a real engine (research, tailoring, Excel store, prep).
"""

import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from core import database, profile, goals, master_cv as M
from departments.orchestrator.agents import Orchestrator
from departments.application.fast_apply import FastApplyQueue
from departments.analytics.agents import AnalyticsAgent
from departments.resume_factory.tailor import ResumeFactory, ats_score, _jd_keywords
from departments.outreach.letters import cover_letter, referral_email
from departments.tracking.app_store import ApplicationStore
from departments.interview.prep import InterviewPrep

st.set_page_config(page_title="CareerOS", page_icon="🎯", layout="wide",
                   initial_sidebar_state="expanded")

THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
:root{
  --bg:#f6f8fd; --panel:#ffffff; --line:#e7ecf5; --ink:#161c2d; --mut:#6b7689;
  --indigo:#6366f1; --sky:#0ea5e9; --pink:#ec4899; --green:#10b981;
  --amber:#f59e0b; --red:#ef4444; --violet:#8b5cf6;
}
/* hide the black Streamlit top toolbar/header */
header[data-testid="stHeader"]{ background:transparent !important; }
[data-testid="stToolbar"]{ right:8px; }

.stApp{ background:
  radial-gradient(1200px 560px at 88% -10%, rgba(139,92,246,.16), transparent 60%),
  radial-gradient(1000px 520px at -8% 4%, rgba(14,165,233,.15), transparent 58%),
  radial-gradient(820px 540px at 50% 118%, rgba(236,72,153,.12), transparent 60%),
  var(--bg); color:var(--ink); font-family:'Inter',sans-serif; }
.block-container{ padding-top:1rem; max-width:1200px; }
h1,h2,h3,h4{ font-family:'Sora',sans-serif !important; color:var(--ink); letter-spacing:-.02em; }
p,span,label,li,div{ color:var(--ink); }
.stCaption,[data-testid="stCaptionContainer"]{ color:var(--mut) !important; }

section[data-testid="stSidebar"]{ background:linear-gradient(180deg,#ffffff,#f4f7fe);
  border-right:1px solid var(--line); }
section[data-testid="stSidebar"] *{ font-family:'Sora',sans-serif; color:var(--ink); }

/* ANIMATED HERO */
.hero{ border:1px solid var(--line); border-radius:22px; padding:26px 30px; margin-bottom:20px;
  background:linear-gradient(120deg,#eef1ff,#e6f6ff,#ffeef7,#f1ecff,#eef1ff);
  background-size:300% 300%; animation:flow 15s ease infinite; position:relative; overflow:hidden;
  box-shadow:0 14px 50px rgba(99,102,241,.10); }
.hero:after{ content:''; position:absolute; right:-30px; top:-40px; width:240px; height:240px;
  background:radial-gradient(circle, rgba(236,72,153,.22), transparent 70%); animation:float 9s ease-in-out infinite; }
.hero:before{ content:''; position:absolute; left:30%; bottom:-60px; width:200px; height:200px;
  background:radial-gradient(circle, rgba(14,165,233,.20), transparent 70%); animation:float 11s ease-in-out infinite reverse; }
@keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(-22px,18px)}}
.hero h1{ margin:0; font-size:32px; font-weight:800; position:relative; z-index:1;
  background:linear-gradient(90deg,var(--indigo),var(--sky),var(--pink),var(--indigo));
  background-size:300% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  animation:shine 6s linear infinite; }
@keyframes shine{to{background-position:300% center}}
.hero p{ margin:.4rem 0 0; color:var(--mut); position:relative; z-index:1; }

/* METRIC CARDS */
.cards{ display:grid; grid-template-columns:repeat(auto-fit,minmax(155px,1fr)); gap:15px; }
.card{ background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:22px;
  text-align:center; box-shadow:0 8px 24px rgba(22,28,45,.06); animation:rise .55s ease both; transition:.25s; position:relative; overflow:hidden; }
.card:before{ content:''; position:absolute; inset:0 0 auto 0; height:3px;
  background:linear-gradient(90deg,var(--indigo),var(--pink)); transform:scaleX(0); transform-origin:left; transition:.3s; }
.card:hover{ transform:translateY(-6px); box-shadow:0 20px 44px rgba(99,102,241,.20); }
.card:hover:before{ transform:scaleX(1); }
.num{ font-family:'Sora'; font-size:34px; font-weight:800;
  background:linear-gradient(90deg,var(--indigo),var(--pink)); -webkit-background-clip:text;
  -webkit-text-fill-color:transparent; }
.lbl{ font-size:11px; color:var(--mut); text-transform:uppercase; letter-spacing:.11em; font-weight:700; }
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}

/* JOB CARDS */
.jcard{ background:var(--panel); border:1px solid var(--line); border-left:4px solid var(--indigo);
  border-radius:16px; padding:16px 18px; margin-bottom:12px; box-shadow:0 6px 18px rgba(22,28,45,.05);
  animation:rise .45s ease both; transition:.22s; }
.jcard:hover{ transform:translateX(5px); border-left-color:var(--pink); box-shadow:0 12px 30px rgba(236,72,153,.14); }
.pill{ display:inline-block; padding:3px 12px; border-radius:999px; font-size:12px; font-weight:700; margin-right:7px; }
.p-green{ background:rgba(16,185,129,.15); color:#047857; }
.p-amber{ background:rgba(245,158,11,.18); color:#b45309; }
.p-red{ background:rgba(239,68,68,.15); color:#b91c1c; }
.p-flag{ background:linear-gradient(90deg,rgba(99,102,241,.18),rgba(236,72,153,.18)); color:#4338ca; }
.gauge{ font-family:'Sora'; font-size:56px; font-weight:800; line-height:1; }

/* BUTTONS — fix the black-on-black bug, force readable styles */
.stButton>button, .stDownloadButton>button{
  background:#ffffff !important; color:var(--ink) !important;
  border:1.5px solid var(--line) !important; border-radius:12px !important;
  font-weight:600 !important; font-family:'Sora',sans-serif !important;
  box-shadow:0 3px 10px rgba(22,28,45,.05) !important; transition:.2s !important; }
.stButton>button:hover, .stDownloadButton>button:hover{
  border-color:var(--indigo) !important; color:var(--indigo) !important;
  transform:translateY(-2px) !important; box-shadow:0 8px 20px rgba(99,102,241,.18) !important; }
/* primary buttons get the gradient */
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"]{
  background:linear-gradient(90deg,var(--indigo),var(--sky)) !important;
  color:#ffffff !important; border:none !important;
  box-shadow:0 8px 22px rgba(99,102,241,.32) !important; }
.stButton>button[kind="primary"]:hover{ filter:brightness(1.07); transform:translateY(-2px) !important; color:#fff !important; }
/* link buttons (Open application) — make them a clear gradient, never black */
.stLinkButton>a{
  background:linear-gradient(90deg,var(--violet),var(--pink)) !important;
  color:#ffffff !important; border:none !important; border-radius:12px !important;
  font-weight:600 !important; font-family:'Sora',sans-serif !important;
  box-shadow:0 8px 22px rgba(139,92,246,.30) !important; transition:.2s !important; }
.stLinkButton>a:hover{ filter:brightness(1.08); transform:translateY(-2px); color:#fff !important; }
.stLinkButton>a *{ color:#fff !important; }

/* inputs */
.stTextInput>div>div>input, .stTextArea textarea, .stNumberInput input{
  border-radius:12px !important; border:1.5px solid var(--line) !important; background:#fff !important; color:var(--ink) !important; }
.stProgress>div>div>div{ background:linear-gradient(90deg,var(--indigo),var(--pink)) !important; }
.stDataFrame{ border-radius:14px; overflow:hidden; }
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)

database.init_db()
queue = FastApplyQueue()
analytics = AnalyticsAgent()
store = ApplicationStore()

# ---- sidebar nav ----
with st.sidebar:
    st.markdown("## 🎯 CareerOS")
    st.caption(profile.NAME)
    page = st.radio("nav", [
        "Overview", "My Loops", "Board", "All Matches", "My Applications",
        "Questions", "CV Checker", "CV Builder", "Cover Letter",
        "Templates", "Inbox", "Interview Prep", "NHS Jobs"], label_visibility="collapsed")
    st.divider()
    st.caption("Prepares, researches & opens.\nYou click send.")


def cards(pairs):
    html = "<div class='cards'>"
    for lbl, val in pairs:
        html += f"<div class='card'><div class='num'>{val}</div><div class='lbl'>{lbl}</div></div>"
    st.markdown(html + "</div>", unsafe_allow_html=True)


def job_cards(items, apply=True):
    from departments.job_intelligence.freshness import freshness_label
    for p in items:
        g = p["ghost"] or 0
        gc, gt = (("p-red", f"ghost {g:.0f}") if g >= 50 else
                  ("p-amber", f"ghost {g:.0f}") if g >= 30 else
                  ("p-green", f"ghost {g:.0f}"))
        flag = "<span class='pill p-flag'>HIGH PRIORITY</span>" if p["verdict"] == "flag" else ""
        fl = p.get("freshness", "")
        fresh = ("<span class='pill p-green'>🔥 24h</span>" if fl == "24h" else
                 "<span class='pill p-amber'>this week</span>" if fl == "this week" else "")
        st.markdown(f"<div class='jcard'>{flag}{fresh}<span class='pill {gc}'>{gt}</span>"
                    f"<span class='pill p-green'>{p['score']}/10</span><br>"
                    f"<b style='font-size:16px'>{p['title']}</b> — {p['company']}<br>"
                    f"<span style='color:#7d8aa0'>{p['location']}</span></div>",
                    unsafe_allow_html=True)
        if not apply:
            continue
        c1, c2, c3 = st.columns([2, 2, 1])
        rp = ROOT / "storage" / "resumes" / str(p["cv"])
        if rp.exists():
            with open(rp, "rb") as fh:
                c1.download_button("Tailored CV (.docx)", fh.read(), file_name=str(p["cv"]),
                                   key=f"cv_{p['job_id']}", use_container_width=True)
        else:
            c1.caption(f"CV: {p['cv']}")
        c2.link_button("Open application", p["url"], use_container_width=True)
        if c3.button("I applied", key=f"ap_{p['job_id']}", use_container_width=True):
            store.record(p["job_id"], resume_name=str(p["cv"]), status="applied")
            st.toast(f"Logged: {p['company']}"); st.rerun()


# ===================== OVERVIEW =====================
if page == "Overview":
    wk = goals.this_week(); goal = goals.get_goal()
    st.markdown(f"<div class='hero'><h1>Good to see you, {profile.NAME.split()[0]}</h1>"
                f"<p>Week of {wk['week_start']} – {wk['week_end']} · "
                f"{wk['applied']} applied · goal {goal if goal else 'not set'}</p></div>",
                unsafe_allow_html=True)
    if not goal:
        st.caption("Set a weekly goal — job seekers who do are more likely to land interviews.")
        g = st.number_input("Weekly application goal", 1, 100, 10)
        if st.button("Set goal", type="primary"):
            goals.set_goal(g); st.rerun()
    else:
        st.progress(min(1.0, wk["applied"] / goal), text=f"{wk['applied']}/{goal} this week")
    st.markdown("#### This week")
    cards([("Applications", wk["applied"]), ("Interviews", wk["interviews"]),
           ("Saved jobs", wk["saved"])])
    st.markdown("#### All-time funnel")
    a = analytics.run()
    cards([("Found", a["jobs_found"]), ("Applied", a["applied"]),
           ("Contacted", a["contacted"]), ("Interviews", a["interviews"]),
           ("Offers", a["offers"])])


# ===================== MY LOOPS =====================
elif page == "My Loops":
    st.markdown("<div class='hero'><h1>My Loops</h1><p>Run the full search, "
                "verify, score and tailor pipeline.</p></div>", unsafe_allow_html=True)
    where = st.text_input("Location filter (blank = UK-wide)", "")
    if st.button("🔍 Run loop now", type="primary"):
        with st.spinner("Searching, ghost-checking, tailoring resumes..."):
            res = Orchestrator().run(where=where.strip())
        st.success(f"Prepared {len(res['prepared'])} application(s). See All Matches.")


# ===================== BOARD =====================
elif page == "Board":
    st.markdown("<div class='hero'><h1>Board</h1><p>Your pipeline at a glance.</p></div>",
                unsafe_allow_html=True)
    s = database.get_session()
    rows = (s.query(database.Job, database.Application)
            .join(database.Application, database.Job.id == database.Application.job_id).all())
    s.close()
    buckets = {"matched": [], "applied": [], "interview": [], "offer": [], "rejected": []}
    for job, app in rows:
        buckets.setdefault(app.status, []).append(job)
    cols = st.columns(5)
    for col, status in zip(cols, ["matched", "applied", "interview", "offer", "rejected"]):
        col.markdown(f"**{status.title()}** ({len(buckets.get(status, []))})")
        for job in buckets.get(status, []):
            col.markdown(f"<div class='jcard' style='padding:10px'><b>{job.title}</b><br>"
                         f"<span style='color:#7d8aa0'>{job.company}</span></div>",
                         unsafe_allow_html=True)


# ===================== ALL MATCHES =====================
elif page == "All Matches":
    st.markdown("<div class='hero'><h1>All Matches</h1><p>Prepared and ranked by fit.</p></div>",
                unsafe_allow_html=True)
    pending = [p for p in queue.pending() if p["status"] != "applied"]
    st.caption(f"{len(pending)} ready")
    if not pending:
        st.info("Nothing yet — run a loop in My Loops.")
    job_cards(pending)


# ===================== MY APPLICATIONS =====================
elif page == "My Applications":
    st.markdown("<div class='hero'><h1>My Applications</h1><p>Everything you've sent — "
                "with contact, resume and status. Export to Excel.</p></div>",
                unsafe_allow_html=True)
    rows = store.rows()
    applied_rows = [r for r in rows if r["Status"] == "applied"]
    cc1, cc2 = st.columns([1, 4])
    if cc1.button("⬇ Export Excel", type="primary"):
        path = store.export_excel()
        with open(path, "rb") as fh:
            st.download_button("Download applications.xlsx", fh.read(),
                               file_name="applications.xlsx", key="xl")
    st.caption(f"{len(applied_rows)} applied")
    if rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Nothing applied yet.")
    # add contact details to an application
    st.markdown("#### Add a contact to an application")
    s = database.get_session()
    apps = (s.query(database.Job, database.Application)
            .join(database.Application, database.Job.id == database.Application.job_id)
            .filter(database.Application.status == "applied").all())
    s.close()
    if apps:
        labels = {f"{j.title} — {j.company}": j.id for j, a in apps}
        pick = st.selectbox("Application", list(labels.keys()))
        name = st.text_input("Contact name")
        li = st.text_input("Contact LinkedIn URL")
        if st.button("Save contact"):
            store.record(labels[pick], contact_name=name, contact_linkedin=li,
                         status="applied")
            st.toast("Contact saved"); st.rerun()


# ===================== QUESTIONS =====================
elif page == "Questions":
    st.markdown("<div class='hero'><h1>Questions</h1><p>Answered once, auto-filled "
                "across applications.</p></div>", unsafe_allow_html=True)
    for key, val in queue.screening_preview().items():
        st.text_input(key.replace("_", " ").title(), value=val, key=f"q_{key}")
    st.caption("Permanent edits go in core/screening.py.")


# ===================== CV CHECKER (real ATS) =====================
elif page == "CV Checker":
    st.markdown("<div class='hero'><h1>ATS Score Checker</h1><p>Paste a job "
                "description. We parse it the way an ATS does, then score your "
                "CV's real coverage — and show exactly what's missing.</p></div>",
                unsafe_allow_html=True)
    from departments.resume_factory.ats_engine import score_cv, cv_text_from_master
    jd = st.text_area("Paste the job description", height=200,
                      placeholder="Paste the full job description here...")
    use_master = st.checkbox("Score my master CV", value=True)
    own = ""
    if not use_master:
        own = st.text_area("Or paste your CV text", height=160)
    if st.button("Run ATS check", type="primary") and jd.strip():
        cv_text = cv_text_from_master() if use_master else own.lower()
        res = score_cv(jd, cv_text)
        score = res["score"]
        colour = ("#10b981" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"<div class='card'><div class='gauge' style='color:{colour}'>"
                        f"{score}<span style='font-size:20px'>/100</span></div>"
                        f"<div class='lbl'>{res['band']} match</div></div>",
                        unsafe_allow_html=True)
        with c2:
            st.progress(score / 100)
            st.caption(f"Matched {len(res['matched'])} of "
                       f"{len(res['matched']) + len(res['missing'])} key terms "
                       f"the job emphasises.")
        st.markdown("#### ✅ Matched keywords")
        st.markdown(" ".join(f"<span class='pill p-green'>{k}</span>"
                             for k in res["matched"]) or "—", unsafe_allow_html=True)
        st.markdown("#### ⚠️ Missing — add these to lift your score")
        if res["missing"]:
            st.markdown(" ".join(f"<span class='pill p-red'>{k}</span>"
                                 for k in res["missing"]), unsafe_allow_html=True)
            st.caption("Only add what's genuinely true for you. Missing terms you "
                       "do have → put them in your skills section in master_cv.py.")
        else:
            st.success("No important gaps — strong coverage for this role.")


# ===================== CV BUILDER =====================
elif page == "CV Builder":
    st.markdown("<div class='hero'><h1>CV Builder</h1><p>Fresh ATS-safe .docx, "
                "tailored from your real CV to the job you paste.</p></div>",
                unsafe_allow_html=True)
    a, b = st.columns(2)
    title = a.text_input("Job title", "AI Engineer")
    company = b.text_input("Company", "Target Company")
    jd = st.text_area("Job description", height=160)
    if st.button("Build tailored CV", type="primary") and jd.strip():
        r = ResumeFactory().build({"title": title, "company": company, "description": jd})
        st.success(f"ATS keywords covered: {r['ats_covered']} · projects: {', '.join(r['projects'])}")
        rp = Path(r["docx"])
        with open(rp, "rb") as fh:
            st.download_button("⬇ Download tailored CV (.docx)", fh.read(),
                               file_name=rp.name, type="primary")


# ===================== COVER LETTER =====================
elif page == "Cover Letter":
    st.markdown("<div class='hero'><h1>Cover Letter</h1><p>Researched opening line "
                "from the company's real work. Regenerate if you don't like it.</p></div>",
                unsafe_allow_html=True)
    a, b = st.columns(2)
    title = a.text_input("Job title", "AI Engineer", key="clt")
    company = b.text_input("Company", "Target Company", key="clc")
    jd = st.text_area("Job description (optional)", height=110)
    if st.button("Draft (with research)", type="primary"):
        with st.spinner(f"Researching {company}..."):
            letter = cover_letter({"title": title, "company": company, "description": jd})
        st.session_state["cl"] = letter
    if "cl" in st.session_state:
        st.text_area("Draft — edit freely", st.session_state["cl"], height=380, key="cltext")


# ===================== TEMPLATES (referral) =====================
elif page == "Templates":
    st.markdown("<div class='hero'><h1>Smart Referral Emails</h1><p>CareerOS researches "
                "the contact and company first, then drafts. You send.</p></div>",
                unsafe_allow_html=True)
    a, b = st.columns(2)
    contact = a.text_input("Contact name", "")
    company = b.text_input("Company", "Target Company", key="tc")
    title = a.text_input("Role", "AI Engineer", key="tt")
    linkedin = b.text_input("Contact LinkedIn URL (optional)", "")
    if st.button("Research & draft referral", type="primary"):
        with st.spinner(f"Researching {contact or 'contact'} and {company}..."):
            res = referral_email(contact, {"title": title, "company": company}, linkedin)
        st.session_state["ref"] = res
    if "ref" in st.session_state:
        res = st.session_state["ref"]
        ru = res["research_used"]
        st.caption(f"Research: company {'✓ found' if ru['company_found'] else '— not found'}, "
                   f"contact {'✓ found' if ru['person_found'] else '— limited'}")
        st.text_area("Referral email — review & edit", res["email"], height=340, key="reftext")
        if ru["company_sources"]:
            st.caption("Sources: " + " · ".join(ru["company_sources"][:3]))


# ===================== INBOX =====================
elif page == "Inbox":
    st.markdown("<div class='hero'><h1>Inbox</h1><p>Read-only Gmail scan — "
                "auto-detects interview, offer and rejection emails.</p></div>",
                unsafe_allow_html=True)
    from departments.tracking.gmail_connector import GmailConnector
    gc = GmailConnector()
    if not gc.connected():
        st.info("Gmail not connected yet. One-time setup:\n\n"
                "1. Put your Google OAuth `credentials.json` in the project root.\n"
                "2. In PowerShell run: `python -m departments.tracking.gmail_connector`\n"
                "3. Approve read-only access in the browser. Done — refresh this page.")
    else:
        if st.button("📨 Scan my inbox", type="primary"):
            with st.spinner("Reading recent job-related mail (read-only)..."):
                st.session_state["mail"] = gc.scan()
        if "mail" in st.session_state:
            res = st.session_state["mail"]
            if res.get("error"):
                st.error(res["error"])
            events = res.get("events", [])
            # summary counts by category
            counts = {"applied": 0, "interview": 0, "offer": 0, "rejection": 0}
            for e in events:
                counts[e["label"]] = counts.get(e["label"], 0) + 1
            st.markdown("<div class='cards'>"
                        + "".join(f"<div class='card'><div class='num'>{counts[k]}</div>"
                                  f"<div class='lbl'>{k}</div></div>"
                                  for k in ("applied", "interview", "offer", "rejection"))
                        + "</div>", unsafe_allow_html=True)
            st.caption(f"Scanned {res.get('scanned', 0)} messages · "
                       f"{len(events)} job-relevant found")
            colour = {"interview": "p-flag", "offer": "p-green",
                      "rejection": "p-red", "applied": "p-amber"}
            for e in events:
                st.markdown(
                    f"<div class='jcard'><span class='pill {colour.get(e['label'],'p-amber')}'>"
                    f"{e['label'].upper()}</span><br>"
                    f"<b>{e['subject']}</b><br>"
                    f"<span style='color:#6b7689'>{e['from']} · {e['date']}</span><br>"
                    f"<span style='color:#6b7689'>{e['snippet']}</span></div>",
                    unsafe_allow_html=True)
            if not events:
                st.info("Nothing job-related found. If you've applied recently, the "
                        "confirmation email may use wording the filter misses — tell "
                        "the developer the subject line and it'll be added.")


# ===================== INTERVIEW PREP =====================
elif page == "Interview Prep":
    st.markdown("<div class='hero'><h1>Interview Prep</h1><p>Researches the company A–Z "
                "and uses the exact CV you sent for that job.</p></div>", unsafe_allow_html=True)
    s = database.get_session()
    apps = (s.query(database.Job, database.Application)
            .join(database.Application, database.Job.id == database.Application.job_id)
            .filter(database.Application.status == "applied").all())
    s.close()
    if not apps:
        st.info("Apply to a job first — prep is built around the role you applied to.")
    else:
        labels = {f"{j.title} — {j.company}": j.id for j, a in apps}
        pick = st.selectbox("Which application?", list(labels.keys()))
        if st.button("Build prep brief (with research)", type="primary"):
            with st.spinner("Researching the company and role..."):
                brief = InterviewPrep().build(labels[pick])
            st.session_state["brief"] = brief
        if "brief" in st.session_state:
            b = st.session_state["brief"]
            st.markdown(f"**Resume you used:** {b['resume_used']}")
            st.markdown(f"#### {b['company']} — what they do")
            st.write(b["company_overview"] or "(no public summary found)")
            if b["company_from_site"]:
                st.caption("From their site: " + b["company_from_site"][:400])
            st.markdown("#### Interview signal for this role")
            st.write(b["interview_signal"] or "(no public interview data found)")
            st.markdown("#### Likely rounds")
            st.write(", ".join(b["likely_rounds"]))
            st.markdown("#### Technical topics to prepare")
            for t in b["technical_topics"]:
                st.markdown(f"- {t}")
            st.markdown("#### Questions from your CV")
            for q in b["cv_questions"]:
                st.markdown(f"- {q}")
            st.markdown(f"**Core story:** {b['core_story']}")
            if b["company_sources"]:
                st.caption("Sources: " + " · ".join(b["company_sources"][:3]))

# ===================== NHS JOBS =====================
elif page == "NHS Jobs":
    st.markdown("<div class='hero'><h1>NHS Jobs</h1><p>Healthcare and public-sector "
                "roles, freshest first — scored against your profile.</p></div>",
                unsafe_allow_html=True)
    from departments.job_intelligence.freshness import fetch_nhs, freshness_label, sort_fresh
    from departments.orchestrator.matcher import match
    if st.button("🏥 Find NHS jobs", type="primary"):
        with st.spinner("Searching NHS data/AI/ML roles (last 7 days)..."):
            raw = sort_fresh(fetch_nhs(["NHS data scientist"]))
            # keep only roles the matcher doesn't reject and that score onto the board
            nhs = []
            for j in raw:
                r = match(j)
                if r["verdict"] != "reject":
                    j["_score"] = r["score"]
                    nhs.append(j)
        st.session_state["nhs"] = nhs
    if "nhs" in st.session_state:
        nhs = st.session_state["nhs"]
        if not nhs:
            st.info("No NHS data/AI/ML roles in the last 7 days that match your "
                    "field (or Adzuna keys not set). NHS posts these regularly — "
                    "try again in a few days.")
        st.caption(f"{len(nhs)} relevant NHS roles in your field")
        for j in nhs:
            r = match(j)
            fl = freshness_label(j)
            fresh = ("<span class='pill p-green'>🔥 24h</span>" if fl == "24h" else
                     "<span class='pill p-amber'>this week</span>" if fl == "this week" else "")
            st.markdown(f"<div class='jcard'>{fresh}"
                        f"<span class='pill p-green'>{r['score']}/10</span><br>"
                        f"<b>{j['title']}</b> — {j['company']}<br>"
                        f"<span style='color:#7d8aa0'>{j['location']}</span></div>",
                        unsafe_allow_html=True)
            st.link_button("Open NHS application", j["url"])

st.caption("CareerOS researches, prepares and opens — you review and click send.")
