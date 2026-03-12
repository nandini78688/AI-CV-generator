import streamlit as st
import requests
from pypdf import PdfReader
from docx import Document
import io
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Page config

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🤖",
    layout="wide"
)


# Utility Functions

def query_ollama(messages, model="llama3"):
    url = "http://localhost:11434/api/generate"
    prompt = ""
    for m in messages:
        prompt += f"{m['role'].upper()}: {m['content']}\n"

    payload = {"model": model, "prompt": prompt, "stream": False}

    try:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        return f"Ollama error: {e}"

def extract_text(file):
    try:
        if file.type == "application/pdf":
            data = file.read()
            reader = PdfReader(io.BytesIO(data))
            text = ""
            for p in reader.pages:
                if p.extract_text():
                    text += p.extract_text() + "\n"
            if text.strip():
                return text
            images = convert_from_bytes(data)
            return "".join(pytesseract.image_to_string(i) for i in images)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(io.BytesIO(file.read()))
            return "\n".join(p.text for p in doc.paragraphs)
        elif file.type.startswith("image/"):
            return pytesseract.image_to_string(Image.open(file))
        elif file.type == "text/plain":
            return file.read().decode("utf-8")
    except Exception as e:
        return f"Extraction error: {e}"
    return ""

# -------------------------------
# Session State
# -------------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {1: []}
    st.session_state.current_chat = 1
    st.session_state.chat_id = 1
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# Sidebar
st.sidebar.title("💬 Chat History")
if st.sidebar.button("➕ New Chat"):
    st.session_state.chat_id += 1
    st.session_state.chats[st.session_state.chat_id] = []
    st.session_state.current_chat = st.session_state.chat_id

st.sidebar.divider()
for cid in st.session_state.chats:
    if st.sidebar.button(f"Chat {cid}", key=f"chat_{cid}"):
        st.session_state.current_chat = cid


# Main UI
st.title("🤖 AI Cover Letter & Resume Pro")
st.caption("Generate ATS-optimized documents and analyze job fit.")

current_chat = st.session_state.chats[st.session_state.current_chat]

for msg in current_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Input Form

with st.form("cover_form"):
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. Senior Software Engineer")
        company = st.text_input("Company Name")
        skills = st.text_area("Key Skills (Top 5)")

    with col2:
        experience = st.text_area("Key Achievements")
        uploaded_files = st.file_uploader(
            "📎 Upload Resume & JD",
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

    # Added Mode Selection
    mode = st.radio("What should I generate?", ["Cover Letter", "Optimized Resume Content", "Job Fit Analysis"], horizontal=True)
    submit = st.form_submit_button("Generate Document")

# Logic & Prompt Engineering
if submit:
    if not all([job_title, company]) or not uploaded_files:
        st.warning("Please provide at least the Job Title, Company, and Resume.")
    else:
        file_context = ""
        for f in uploaded_files:
            file_context += extract_text(f) + "\n"

        # Specialized ATS Prompting
        if mode == "Cover Letter":
            system_prompt = f"Create a professional, ATS-friendly cover letter for {job_title} at {company}. Use a modern header, mention specific skills ({skills}), and emphasize achievements ({experience}). Avoid buzzwords. Use a standard business letter format."
        elif mode == "Optimized Resume Content":
            system_prompt = f"Rewrite the following resume content to be ATS-optimized for a {job_title} role at {company}. Use the X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]). Include keywords: {skills}."
        else:
            system_prompt = f"Analyze the match between this resume and the {job_title} role at {company}. Provide a Match Percentage, missing keywords, and 3 tips to improve the resume."

        full_prompt = f"{system_prompt}\n\nContext from Uploads:\n{file_context[:4000]}"
        
        current_chat.append({"role": "user", "content": f"Generate {mode} for {job_title} at {company}"})

        with st.chat_message("assistant"):
            with st.spinner("Processing with AI..."):
                reply = query_ollama([{"role": "user", "content": full_prompt}])
                st.markdown(reply)
                st.session_state.last_response = reply
        
        current_chat.append({"role": "assistant", "content": reply})

# New Features: Download & Actions
if st.session_state.last_response:
    st.divider()
    st.subheader("📄 Export & Actions")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    # Download as TXT (Best for ATS compatibility)
    st.download_button(
        label="📥 Download as Text (ATS Best)",
        data=st.session_state.last_response,
        file_name=f"{job_title}_Document.txt",
        mime="text/plain",
    )
    

    st.info("💡 **ATS Tip:** When saving as PDF, ensure you use a standard font like Arial or Calibri and avoid tables/graphics for the highest parse rate.")
