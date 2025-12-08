Streamlit app link : https://intelligentresumebasedjobsuggestiongit-jyfrxfsd4ccaxhzblg7hcw.streamlit.app

🧠 Intelligent Resume-Based Job Suggestion System
AI-Powered Job Matching using AWS Bedrock, Lambda, MongoDB & Streamlit
  This project intelligently analyzes a user’s resume, extracts skills & experience using AWS Bedrock Claude, retrieves real-time job opportunities using JSearch API,    scores job matches using a hybrid ranking engine, and displays personalized job suggestions through a Streamlit UI.
🚀 Architecture Overview
1️⃣ Resume Upload (Streamlit → S3)
User uploads a resume from Streamlit UI
Resume is stored in S3 bucket
S3 event triggers resume_parser_lambda

2️⃣ Resume Parsing (AWS Lambda + Claude)
Lambda extracts PDF text using PyPDF2
Claude 3 Haiku performs structured JSON parsing
Titan embeddings generated for matching
Data stored in MongoDB Atlas

3️⃣ Job Fetch Lambda (RapidAPI JSearch)
Extracts user’s job title from resume
Queries JSearch API
Performs enrichment with Claude (summaries, key skills)
Deduplicates jobs
Stores top job pool into MongoDB
Invokes job matcher lambda

4️⃣ Job Matcher Lambda
Ranks jobs using hybrid scoring:
final_score =
0.55 * semantic_similarity +
0.25 * keyword_overlap +
0.10 * recency_weight +
0.10 * popularity_score:
Also generates:
Missing skill list
Match explanation using Claude
Top 20 matches stored in DB

5️⃣ Streamlit UI
User sees:
✔ Recommended jobs
✔ Match explanations
✔ Skill-gap heatmap
✔ Clickable job links
✔ Daily Refresh button (API Gateway → Lambda)opularity_score

🛠️ Tech Stack
Cloud & Backend
AWS Lambda
AWS S3
AWS Bedrock (Claude & Titan Embeddings)
AWS API Gateway
MongoDB Atlas

APIs
RapidAPI JSearch

Frontend
Streamlit
Matplotlib / Pandas (skill-gap visualisation)

📦 Installation (Local)
pip install -r requirements.txt
streamlit run app.py

🔐 Streamlit Cloud Secrets

Your .streamlit/secrets.toml must contain:
MONGO_URI="..."
MONGO_DB="..."
AWS_ACCESS_KEY_ID="..."
AWS_SECRET_ACCESS_KEY="..."
AWS_REGION="us-east-1"
S3_BUCKET="..."
RESUME_LAMBDA="..."
UPLOAD_PATH="resumes/"
JOB_REFRESH_ENDPOINT="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/refresh"
RAPIDAPI_KEY="..."

📊 Evaluation Metrics
| Metric                       | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| **Semantic Accuracy**        | Cosine similarity between resume & job embeddings |
| **Skill Gap Detection Rate** | Accuracy of Claude’s missing skill extraction     |
| **Response Time**            | Full pipeline < 8 seconds                         |
| **Job Coverage Ratio**       | Relevant jobs returned / total fetched            |
| **Scalability Score**        | Successful Lambda runs per 1000 uploads           |
| **User Engagement Index**    | % of users clicking through job results           |
