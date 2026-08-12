Capstone Project: AI-Powered Resume Screener
An end-to-end AI platform that parses candidate resumes (PDFs), computes semantic match scores against a job description using local embeddings, and generates automated AI summaries and matched skills via Google Gemini.

# Live Application URLs

- **Frontend Application:** https://betabytez-ai-ml-task5-muhammadmaazshah-njfmjub7oqgbyyjjeuhoxd.streamlit.app
- **Backend API Docs:** https://resumescreener-backend-j872.onrender.com/docs

System Architecture
1. Visual Flow Diagram (Mermaid)
```mermaid
graph TD
    %% Client Layer
    subgraph Client ["Frontend Layer (Streamlit)"]
        UI["User Interface"]
        JD["Job Description Input"]
        PDF["PDF Resumes Upload"]
        Chart["Plotly Analytics Dashboard"]
    end

    %% API Layer
    subgraph Server ["Backend Layer (FastAPI Engine)"]
        API["REST API Endpoint (/api/screen)"]
        Parser["PDF Text Parser (pypdf)"]
        
        subgraph AI_Engine ["Core AI Engine"]
            ST["SentenceTransformers Model<br/>(all-MiniLM-L6-v2)"]
            Cosine["Cosine Similarity Engine<br/>(scikit-learn)"]
            Gemini["LLM Insight Generator<br/>(Google Gemini 2.5 Flash API)"]
        end
    end

    %% Data Flow Connections
    JD --> UI
    PDF --> UI
    UI -- "HTTP POST (FormData)" --> API
    API --> Parser
    Parser -- "Raw Text" --> ST
    ST -- "Vector Embeddings" --> Cosine
    Parser -- "Resume Text + JD" --> Gemini
    Cosine -- "Match Scores (%)" --> API
    Gemini -- "Summaries & Matched Skills" --> API
    API -- "JSON Response" --> UI
    UI --> Chart

2. High-Level Pipeline ASCII View
Plaintext
+-----------------------------------------------------------------------------------+
|                                Streamlit Frontend                                 |
|   - Job Description Textarea                                                     |
|   - Multi-PDF File Uploader                                                       |
|   - Plotly Bar Chart & Score Distribution View                                    |
+-----------------------------------------+-----------------------------------------+
                                          |
                                HTTP POST /api/screen
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                 FastAPI Backend                                   |
|                                                                                   |
|  1. Text Parsing      : Extracts readable text from PDF buffers via PyPDF.         |
|  2. Vector Embedding  : Generates 384-d vectors using `all-MiniLM-L6-v2`.         |
|  3. Context Matching  : Calculates Cosine Similarity between JD and Resumes.     |
|  4. LLM Analysis      : Queries Gemini 2.5 Flash for fit summary & key skills.   |
+-----------------------------------------------------------------------------------+

Key Features
Semantic Candidate Matching: Evaluates context similarity using HuggingFace all-MiniLM-L6-v2 embeddings instead of basic keyword matching.

Interactive Analytics: Visualizes score distributions across candidates with interactive Plotly bar charts.
AI Candidate Insights: Uses Google Gemini 2.5 Flash to extract key matched skills and concise fit summaries.
Decoupled Architecture: Clean separation with FastAPI REST backend and Streamlit UI frontend.

Tech Stack
Backend: FastAPI, Uvicorn, PyPDF, Sentence-Transformers, Scikit-Learn, Google GenAI SDK
Frontend: Streamlit, Plotly, Pandas, Requests
Core AI Engine: HuggingFace all-MiniLM-L6-v2 + Gemini 2.5 Flash

Local Setup Instructions
1. Clone Repository
Bash
git clone [https://github.com/your-username/betabytez-aiml-task5-muhammadmaazshah.git](https://github.com/your-username/betabytez-aiml-task5-muhammadmaazshah.git)
cd betabytez-aiml-task5-muhammadmaazshah

2. Configure Backend
Bash
cd backend
pip install -r requirements.txt
Create a .env file inside backend/:

Code snippet
GOOGLE_API_KEY=your_gemini_api_key_here
Run FastAPI server:

Bash
python -m uvicorn main:app --reload
3. Configure Frontend
Open a new terminal tab and navigate to frontend/:

Bash
cd frontend
pip install -r requirements.txt
streamlit run app.py

System Analysis & Performance Evaluation
1. Semantic Vector Embeddings vs. Keyword Matching
Contextual Accuracy: By embedding text into 384-dimensional dense vectors using `all-MiniLM-L6-v2`, the system captures underlying semantic context rather than relying on exact string matching. For example, it correctly maps equivalent concepts like *"Flutter Developer"* and *"Mobile Application Engineer"*.
Similarity Scoring: Cosine similarity generates a continuous score spectrum ($0\% \text{ to } 100\%$), preventing artificial score inflation from keyword-stuffed CVs while penalizing incomplete resumes.

2. LLM Latency & Processing Pipeline
Optimized Context Window: Truncating text payloads sent to Gemini 2.5 Flash minimizes token consumption while retaining core skill sets and candidate experience highlights.
Execution Speed: Local vector calculations execute within milliseconds, while LLM summaries add ~1–2 seconds per candidate, ensuring scalability for bulk PDF screening.

3. Known Limitations & Potential Enhancements
PDF Extraction Boundary: Relies on readable text extraction via `pypdf`. Image-based scanned PDFs require an Optical Character Recognition (OCR) pipeline like `pytesseract`.
Granular Weighting: Currently measures global document similarity. Future iterations can introduce explicit sub-scoring for years of experience, degree level, and specific technical tools.

Conclusion
The AI-Powered Resume Screener successfully bridges classical NLP embeddings with generative LLMs to automate preliminary candidate vetting. Decoupling local embedding calculations (FastAPI backend) from dynamic UI analytics (Streamlit frontend) provides an efficient, objective, and visual solution that significantly reduces HR screening overhead while delivering context-aware candidate rankings.