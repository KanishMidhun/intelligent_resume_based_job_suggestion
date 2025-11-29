import streamlit as st

MONGO_URI = st.secrets["MONGO_URI"]
MONGO_DB = st.secrets["MONGO_DB"]
S3_BUCKET = st.secrets["S3_BUCKET"]
AWS_REGION = st.secrets["AWS_REGION"]
MATCHES_COLLECTION = "matches"
RESUMES_COLLECTION = "resumes"
RESUME_LAMBDA = st.secrets["RESUME_LAMBDA"]