import streamlit as st
import requests
from pypdf import PdfReader
from docx import Document
import io
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

# -------------------------------
# Tesseract path (Windows)
# -------------------------------
# Ensure Tesseract is installed at this path or update accordingly
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="AI Career Assistant Pro",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# Utility Functions
# -------------------------------
def query_ollama(messages, model="llama3"):
    url = "http://localhost:11434/api/generate"
    prompt = ""
    for m in messages:
        role = m['role'].upper()
        prompt += f"{role}: {m['content']}\n"

    payload = {"model": model, "prompt": prompt, "stream": False}

    try:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        return f"Ollama error: {e}. Ensure Ollama is running locally."

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
            # Fallback to OCR if PDF is scanned/image-based
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

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.title("💬 Chat History")
    if st.button("➕ New Chat"):
        st.session_state.chat_id += 1
        st.session_state.chats[st.session_state.chat_id] = []
        st.session_state.current_chat = st.session_state.chat_id

    st.divider()
    for cid in list(st.session_state.chats.keys()):
        if st.button(f"Chat {cid}", key=f"chat_btn_{cid}"):
            st.session_state.current_chat = cid
    
    st.divider()
    st.info("💡 **Pro Tip:** Use 'Interview Prep' after generating a Cover Letter to get questions based on your specific claims.")

# -------------------------------
# Main UI
# -------------------------------
st.title("🤖 AI Cover Letter & Resume Pro")
st.caption("Generate ATS-optimized documents and prepare for the interview.")

current_chat = st.session_state.chats[st.session_state.current_chat]

# Display Chat History
for msg in current_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# Input Form
# -------------------------------
with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. Senior Software Engineer")
        company = st.text_input("Company Name", placeholder="e.g. Google")
        skills = st.text_area("Key Skills (comma separated)", placeholder="Python, AWS, Project Management...")

    with col2:
        experience = st.text_area("Key Achievements", placeholder="Reduced latency by 20%, Managed team of 5...")
        uploaded_files = st.file_uploader(
            "📎 Upload Resume & JD",
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

    mode = st.radio(
        "Select Action:", 
        ["Cover Letter", "Optimized Resume Content", "Job Fit Analysis", "Interview Prep"], 
        horizontal=True
    )
    
    submit = st.form_submit_button("Generate Output")

# -------------------------------
# Logic & Prompt Engineering
# -------------------------------
if submit:
    if not all([job_title, company]) or not uploaded_files:
        st.warning("Please provide the Job Title, Company, and at least one file (Resume).")
    else:
        file_context = ""
        for f in uploaded_files:
            file_context += extract_text(f) + "\n"

        # Specialized Prompt Logic
        if mode == "Cover Letter":
            system_prompt = (
                f"Create a professional, ATS-friendly cover letter for {job_title} at {company}. "
                f"Incorporate these skills: {skills}. Highlight these achievements: {experience}. "
                "Use standard business formatting."
            )
        elif mode == "Optimized Resume Content":
            system_prompt = (
                f"Rewrite the uploaded resume content for a {job_title} role at {company}. "
                "Use the Google X-Y-Z formula (Accomplished X, as measured by Y, by doing Z). "
                f"Ensure keywords like {skills} are naturally integrated."
            )
        elif mode == "Job Fit Analysis":
            system_prompt = (
                f"Act as an expert Recruiter. Analyze the match between the resume and the {job_title} role at {company}. "
                "Provide a Match Score (0-100%), identify missing keywords, and give 3 actionable improvements."
            )
        elif mode == "Interview Prep":
            system_prompt = (
                f"Based on the resume context and the {job_title} role at {company}, generate: "
                "1. Five behavioral interview questions based on the achievements mentioned. "
                "2. Three technical or role-specific questions. "
                "3. For each question, provide a 'Suggested Answer Strategy' using the STAR method."
            )

        full_prompt = f"{system_prompt}\n\nContext from Uploads:\n{file_context[:4000]}"
        
        # Update Session Chat
        current_chat.append({"role": "user", "content": f"Generate {mode} for {job_title}"})

        with st.chat_message("assistant"):
            with st.spinner(f"AI is working on your {mode}..."):
                reply = query_ollama([{"role": "user", "content": full_prompt}])
                st.markdown(reply)
                st.session_state.last_response = reply
        
        current_chat.append({"role": "assistant", "content": reply})

# -------------------------------
# Export & Action Section
# -------------------------------
if st.session_state.last_response:
    st.divider()
    st.subheader("📄 Export & Next Steps")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.download_button(
            label="📥 Download Result (.txt)",
            data=st.session_state.last_response,
            file_name=f"{job_title.replace(' ', '_')}_{mode.replace(' ', '_')}.txt",
            mime="text/plain",
        )
    
    with c2:
        if mode != "Interview Prep":
            if st.button("🎯 Generate Interview Questions for this document"):
                # Force a new prompt based on the specific text just generated
                prep_context = f"Here is a document: {st.session_state.last_response}. Based on this, what are 5 interview questions I should prepare for?"
                with st.spinner("Analyzing document for questions..."):
                    q_reply = query_ollama([{"role": "user", "content": prep_context}])
                    st.session_state.last_response = q_reply
                    current_chat.append({"role": "assistant", "content": q_reply})
                    st.rerun()

    st.info("💡 **Note:** Plain text files are best for ATS (Applicant Tracking Systems) to ensure your formatting doesn't get scrambled.")
