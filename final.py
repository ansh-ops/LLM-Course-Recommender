import streamlit as st
import fitz
import faiss
import numpy as np
import json
import pickle
from sentence_transformers import SentenceTransformer

# ------------- Helper Functions -------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_resume_index():
    index = faiss.read_index("resume_index.faiss")
    with open("resume_metadata.json", "r") as f:
        resumes = json.load(f)
    return index, resumes

@st.cache_resource
def load_course_index():
    index = faiss.read_index("courses_index.faiss")
    with open("courses_metadata.pkl", "rb") as f:
        courses = pickle.load(f)
    return index, courses

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return " ".join(page.get_text() for page in doc)

# ------------- Load Models and Indexes -------------
model = load_model()
resume_index, resume_metadata = load_resume_index()
course_index, course_metadata = load_course_index()

# ------------- Streamlit UI -------------
st.title("📚 LLM-Powered Resume & Course Recommender")
st.write("Upload your resume to see similar candidate profiles and get personalized course recommendations.")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    # Extract text
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    # Generate embedding
    query_embedding = model.encode([resume_text])

    # ------------- Resume Matching -------------
    st.subheader("👥 Top Matching Profiles")
    k=5
    D_res, I_res = resume_index.search(np.array(query_embedding), k)
    for i in I_res[0]:
        profile = resume_metadata[i]
        st.markdown(f"**Name**: {profile.get('name', 'N/A')}")
        st.write(profile.get('text', 'No content available'))
        st.markdown("---")

    # ------------- Course Recommendations -------------
    st.subheader("📘 Recommended Courses")
    k=3
    D_crs, I_crs = course_index.search(np.array(query_embedding), k)
    for i in I_crs[0]:
        course = course_metadata[i]
        st.markdown(f"**{course['Course Name']}**")
        st.write(course['Course Description'])
        st.markdown("---")
