🤖 AI Career Assistant: Privacy-First CV Generator

AI Career Assistant (v1.0) is a local-first, LLM-powered engine developed by Nandini to bridge the gap between candidates and Applicant Tracking Systems (ATS). By leveraging local inference via Ollama, this CV Generator ensures your most sensitive data—your career history—never leaves your machine.

🌟 Key Features

📄 Intelligent CV & Cover Letter Synthesis: Context-aware generation matching your unique skills to specific Job Descriptions (JD) and company cultures.

📈 X-Y-Z Resume Refactoring: Nandini's implementation of the "Google X-Y-Z" formula ($Accomplished [X] \text{ as measured by } [Y], \text{ by doing } [Z]$) for maximum professional impact.

🔍 Semantic Job Fit Analysis: Provides a quantitative match score, identifies missing keywords, and offers actionable suggestions for improvement.

👁️ OCR Vision Pipeline: Scanned PDF or image? Integrated Tesseract OCR extracts text from image-based documents seamlessly.

🔒 Zero-Trust Privacy: Runs entirely on your local hardware. No OpenAI/Anthropic API keys required, ensuring 100% data sovereignty.

🏗 System Architecture

graph TD
    A[User Files: PDF/DOCX/PNG] --> B{File Type?}
    B -->|Structured Text| C[PyPDF/Docx Parser]
    B -->|Image/Scanned| D[Tesseract OCR Engine]
    C --> E[Text Normalization & Cleaning]
    D --> E
    E --> F[Nandini's Prompt Engine]
    F --> G[Local LLM: Ollama/Llama3]
    G --> H[Streamlit Reactive UI]
    H --> I[ATS-Friendly Export]


🚀 Quick Start

1. Prerequisites

Python 3.9+

Ollama installed and running locally.

Tesseract OCR installed on your system.

2. Installation

# Clone the repository
git clone [https://github.com/nandini-repo/ai-cv-generator.git](https://github.com/nandini-repo/ai-cv-generator.git)
cd ai-cv-generator

# Install dependencies
pip install streamlit 
requests
pypdf
python-docx 
pytesseract
pdf2image
pillow


3. Setup Ollama

Pull the default model optimized for Nandini's engine:

ollama run llama3


4. Run the Application

streamlit run app.py


🧪 The "X-Y-Z" Formula in Action

The engine transforms generic bullet points into high-conversion achievements:

Before: "Managed a team of developers and improved the app."

After: "Accomplished [30% faster feature delivery] as measured by [Jira velocity metrics], by doing [leading a team of 5 in migrating to a Scrum-based CI/CD workflow]."

🛠 Tech Stack

Frontend: Streamlit

Orchestration: Python

LLM Engine: Ollama (Llama3)

OCR/Vision: Tesseract & Pillow

Document Logic: python-docx, pypdf, pdf2image

📄 License

Distributed under the MIT License.

Author: Nandini

Project Link: https://github.com/nandini-repo/ai-cv-generator
