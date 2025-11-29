import streamlit as st
import boto3
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pymongo import MongoClient

st.set_page_config(page_title="AI Job Matcher", layout="wide")

# -----------------------------------------
# LOAD SECRETS (FLAT FORMAT)
# -----------------------------------------
S3_BUCKET = st.secrets["S3_BUCKET"]
RESUME_LAMBDA = st.secrets["RESUME_LAMBDA"]
MONGO_URI = st.secrets["MONGO_URI"]
MONGO_DB = st.secrets["MONGO_DB"]
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = st.secrets.get("AWS_REGION", "us-east-1")
JOB_REFRESH_ENDPOINT = st.secrets.get("JOB_REFRESH_ENDPOINT", "")

UPLOAD_PATH = "resumes/"

# -----------------------------------------
# AWS Clients
# -----------------------------------------
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
s3 = session.client("s3")
lambda_client = session.client("lambda")

# -----------------------------------------
# MongoDB
# -----------------------------------------
mongo = MongoClient(MONGO_URI)
db = mongo[MONGO_DB]

# -----------------------------------------
# Helper Functions
# -----------------------------------------
def upload_resume_to_s3(file, user_email):
    filename = user_email.replace("@", "_") + ".pdf"
    key = UPLOAD_PATH + filename
    s3.upload_fileobj(file, S3_BUCKET, key)
    return key

def trigger_resume_lambda(key, user_email):
    payload = {"s3_key": key, "user_id": user_email}
    lambda_client.invoke(
        FunctionName=RESUME_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )

def trigger_job_fetch(user_email):
    if not JOB_REFRESH_ENDPOINT:
        return {"ok": False, "error": "JOB_REFRESH_ENDPOINT not configured"}
    try:
        r = requests.post(JOB_REFRESH_ENDPOINT, json={"user_id": user_email})
        return {"ok": True, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_matches(user_email):
    doc = db.matches.find_one({"user_id": user_email})
    return doc.get("results", []) if doc else []

def save_feedback(user, job, fb):
    db.feedback.insert_one({
        "user_id": user,
        "title": job["title"],
        "company": job["company"],
        "job_link": job.get("job_link"),
        "feedback": fb,
        "ts": datetime.utcnow()
    })

def plot_skill_gap(missing_lists):
    all_m = []
    for L in missing_lists:
        for x in L:
            if x:
                all_m.append(x.lower())
    if not all_m:
        st.info("No missing skills found.")
        return
    df = pd.Series(all_m).value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(df.index, df.values)
    ax.set_title("Skill Gap Heatmap")
    st.pyplot(fig)

def get_recommended_courses(skills):
    if not skills:
        return []
    q = "+".join(skills[:3])
    try:
        url = f"https://api.coursera.org/api/courses.v1?q=search&query={q}"
        r = requests.get(url)
        data = r.json().get("elements", [])
        out = []
        for c in data[:10]:
            name = c.get("name","Course")
            slug = c.get("slug","")
            link = f"https://www.coursera.org/learn/{slug}" if slug else ""
            out.append({"name": name, "link": link})
        return out
    except:
        return []


# -----------------------------------------
# UI LAYOUT
# -----------------------------------------
st.title("📄 AI Job Matcher Dashboard")

st.sidebar.header("User")
user_email = st.sidebar.text_input("Enter your email", value="")

# ----------- RESUME UPLOAD ------------------
st.header("📤 Upload Your Resume")

uploaded = st.file_uploader("Upload PDF Resume", type=["pdf"])

if uploaded and user_email:
    st.info("Uploading to S3...")
    key = upload_resume_to_s3(uploaded, user_email)
    st.success(f"Uploaded to S3: {key}")

    st.info("Triggering resume processing...")
    trigger_resume_lambda(key, user_email)
    st.success("Resume sent for parsing. Wait 10–15 seconds.")

elif uploaded and not user_email:
    st.warning("Enter email before uploading!")

# ----------- JOB FETCH ------------------
st.header("🔍 Fetch Matching Jobs")

if st.button("Refresh Jobs Now"):
    if not user_email:
        st.error("Enter your email first!")
    else:
        res = trigger_job_fetch(user_email)
        if res["ok"]:
            st.success("Job fetching started. Please wait and click 'Load Matches'.")
        else:
            st.error(f"Error: {res['error']}")

# ----------- LOAD MATCHES ------------------
st.header("🏆 Your Job Matches")

if st.button("Load Matches"):
    matches = get_matches(user_email)
    st.session_state["matches"] = matches

matches = st.session_state.get("matches", [])

if not matches:
    st.info("No matches yet. Upload resume → Refresh Jobs.")
else:
    for i, job in enumerate(matches[:20]):
        st.subheader(f"{i+1}. {job['title']} — {job['company']}")
        if job.get("job_link"):
            st.markdown(f"[🔗 Apply / View Job]({job['job_link']})")
        st.write(job.get("description","")[:500] + "...")

        st.write("**Match Reason:**", job.get("match_reason", "-"))
        st.write("**Missing Skills:**", ", ".join(job.get("missing_skills", [])))

        c1, c2 = st.columns(2)
        if c1.button("👍 Like", key=f"like_{i}"):
            save_feedback(user_email, job, "like")
            st.success("Liked!")
        if c2.button("👎 Dislike", key=f"dislike_{i}"):
            save_feedback(user_email, job, "dislike")
            st.warning("Disliked!")
        st.markdown("---")

# ----------- SKILL GAP HEATMAP -----------
if matches:
    st.header("🔥 Skill-Gap Heatmap")
    all_missing = [m.get("missing_skills", []) for m in matches]
    plot_skill_gap(all_missing)

# ----------- COURSES ------------------
if matches:
    st.header("🎓 Recommended Courses (Coursera)")
    all_missing = list({s for L in all_missing for s in L})
    courses = get_recommended_courses(all_missing)
    for c in courses:
        st.markdown(f"- [{c['name']}]({c['link']})")

