import streamlit as st
import fitz 
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

@st.cache_resource

def load_model_and_index():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("resume_index.faiss")
    with open("resume_metadata.json", "r") as f:
        resumes = json.load(f)
    return model, index, resumes

model, index, resumes = load_model_and_index()

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return " ".join(page.get_text() for page in doc)

st.title("LLM-Powered Resume Matcher")
st.write("Upload your resume (PDF or TXT) to find similar candidate profiles.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    query_embedding = model.encode([resume_text])

    D, I = index.search(np.array(query_embedding), top_k=5)
    matches = [resumes[i] for i in I[0]]

    st.subheader("Top Matching Profiles")
    for match in matches:
        st.markdown(f"### {match['name']}")
        st.write(match['text'])
        st.markdown("---")
