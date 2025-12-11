import streamlit as st
from PyPDF2 import PdfReader
import docx
from bs4 import BeautifulSoup
import subprocess
import re

# -------- Document Text Extraction --------
def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.type == "text/html":
        html = file.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
    else:
        return ""

# -------- Abbreviation Extraction --------
def extract_abbreviations(text):
    # Regex: captures "Full Term (ABBR)"
    pattern = r'([A-Za-z][A-Za-z\s\-]+)\s\(([A-Z]{2,})\)'
    matches = re.findall(pattern, text)
    return {abbr: term.strip() for term, abbr in matches}

# -------- Query Ollama --------
def query_ollama(question, context, model="mistral"):
    prompt = f"Answer the question using the context below:\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )
    return result.stdout.decode()

# -------- Streamlit UI --------
st.title("📚 Document Q&A + Abbreviation Index")

# Sidebar mode selector
mode = st.sidebar.radio("Choose Mode:", ["Q&A", "Abbreviation Index"])

if mode == "Q&A":
    st.header("Ask Questions with Document Context")
    question = st.text_input("Enter your question:")
    uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf", "docx", "html"])

    if st.button("Get Answer"):
        context = ""
        if uploaded_file:
            context = extract_text(uploaded_file)
        answer = query_ollama(question, context)
        st.write("### Answer")
        st.write(answer)

elif mode == "Abbreviation Index":
    st.header("Generate Abbreviation Index from Articles")
    uploaded_files = st.file_uploader("Upload scientific articles", type=["pdf","docx","txt","html"], accept_multiple_files=True)

    if st.button("Generate Index"):
        all_abbreviations = {}
        for file in uploaded_files:
            text = extract_text(file)
            abbrs = extract_abbreviations(text)
            all_abbreviations.update(abbrs)

        if all_abbreviations:
            st.write("### Abbreviation Index")
            for abbr, term in all_abbreviations.items():
                st.write(f"{abbr}: {term}")
        else:
            st.write("No abbreviations found in the uploaded documents.")