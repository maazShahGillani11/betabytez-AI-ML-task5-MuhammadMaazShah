import os
import io
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pypdf import PdfReader
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI-Powered Resume Screener API")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Hugging Face Free Inference API URL for lightweight vector embeddings (No PyTorch/RAM overhead)
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"


def get_hf_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Hugging Face API se embeddings calculate karta hai.
    Local memory (RAM) load zero ho jati hai (Render Free Tier 512MB RAM crash fix).
    """
    try:
        response = requests.post(
            HF_API_URL,
            json={"inputs": texts, "options": {"wait_for_model": True}},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"HF API Error Status: {response.status_code}")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate embeddings via HuggingFace API: {str(e)}"
        )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF file content se text extract karne ke liye helper function."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text.strip()
    except Exception as e:
        return ""


def generate_candidate_insights(job_description: str, resume_text: str) -> dict:
    """Gemini API se candidate ki summary aur extracted matched skills generate karta hai."""
    if not client:
        return {
            "summary": "Gemini API key not configured.",
            "extracted_skills": ["N/A"]
        }

    prompt = f"""
    You are an AI HR assistant. Compare the candidate's resume against the Job Description.

    Job Description:
    {job_description[:1500]}

    Candidate Resume:
    {resume_text[:2000]}

    Provide response in exactly this format:
    Summary: <2-sentence overview of candidate fit>
    Skills: <comma-separated list of key matching skills found>
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text
        
        summary = "Summary generated."
        skills = []
        
        for line in text.split('\n'):
            if line.startswith("Summary:"):
                summary = line.replace("Summary:", "").strip()
            elif line.startswith("Skills:"):
                skills_str = line.replace("Skills:", "").strip()
                skills = [s.strip() for s in skills_str.split(',') if s.strip()]

        return {
            "summary": summary,
            "extracted_skills": skills if skills else ["General Fit"]
        }
    except Exception as e:
        return {
            "summary": "Could not generate AI insights.",
            "extracted_skills": ["Error processing AI analysis"]
        }


@app.get("/")
def home():
    return {"message": "AI Resume Screener FastAPI Backend is Running!"}


@app.post("/api/screen")
async def screen_resumes(
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...)
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    
    if not resumes:
        raise HTTPException(status_code=400, detail="Please upload at least one resume PDF.")

    results = []
    resume_texts = []
    file_names = []

    # 1. Extract text from uploaded PDFs
    for file in resumes:
        contents = await file.read()
        text = extract_text_from_pdf(contents)
        if text:
            resume_texts.append(text)
            file_names.append(file.filename)
        else:
            resume_texts.append("")
            file_names.append(file.filename)

    if not any(resume_texts):
        raise HTTPException(status_code=400, detail="Could not extract text from any uploaded PDF.")

    # 2. Compute Semantic Embeddings via HF API & Cosine Similarity
    jd_embedding = get_hf_embeddings([job_description])
    resume_embeddings = get_hf_embeddings(resume_texts)

    similarity_scores = cosine_similarity(jd_embedding, resume_embeddings)[0]

    # 3. Process each candidate and build response
    for idx, filename in enumerate(file_names):
        score = round(float(similarity_scores[idx]) * 100, 2)
        r_text = resume_texts[idx]
        
        ai_insights = generate_candidate_insights(job_description, r_text) if r_text else {
            "summary": "Failed to read PDF content.",
            "extracted_skills": []
        }

        results.append({
            "candidate_name": filename,
            "match_score": score,
            "summary": ai_insights["summary"],
            "matched_skills": ai_insights["extracted_skills"]
        })

    # Sort results by match score in descending order
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "status": "success",
        "total_candidates": len(results),
        "candidates": results
    }