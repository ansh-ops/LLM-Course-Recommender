import streamlit as st
import fitz
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------- Helpers -----------------
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_course_index():
    index = faiss.read_index("courses_index.faiss")
    with open("courses_metadata.pkl", "rb") as f:
        courses = pickle.load(f)
    return index, courses

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return " ".join(page.get_text() for page in doc)

# Basic keyword-based skill extraction
def extract_skills_from_resume(resume_text, known_skills):
    resume_text_lower = resume_text.lower()
    return [skill for skill in known_skills if skill.lower() in resume_text_lower]

# Maximal Marginal Relevance (MMR) for diverse results
def mmr(query_embedding, candidate_embeddings, k=5, lambda_param=0.5):
    selected = []
    candidates = list(range(len(candidate_embeddings)))

    sim_to_query = cosine_similarity(candidate_embeddings, query_embedding.reshape(1, -1)).flatten()
    sim_between_candidates = cosine_similarity(candidate_embeddings)

    for _ in range(k):
        if not selected:
            idx = np.argmax(sim_to_query)
            selected.append(idx)
            candidates.remove(idx)
        else:
            mmr_score = []
            for candidate in candidates:
                sim_to_selected = max(sim_between_candidates[candidate][selected])
                score = lambda_param * sim_to_query[candidate] - (1 - lambda_param) * sim_to_selected
                mmr_score.append(score)
            idx = candidates[np.argmax(mmr_score)]
            selected.append(idx)
            candidates.remove(idx)

    return selected

# ----------------- Load -----------------
model = load_model()
course_index, course_metadata = load_course_index()

# ----------------- UI -----------------
st.title("📚 LLM-Powered Course Recommender")
st.write("Upload your resume to get personalized and skill-aware course recommendations.")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    # Extract text
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    # Extract current skills
    known_skills = ["Python", "SQL", "TensorFlow", "PyTorch", "AWS", "Docker", 
                    "Java", "React", "NLP", "Spark", "Hadoop", "Tableau"]
    resume_skills = extract_skills_from_resume(resume_text, known_skills)

    st.subheader("🧠 Extracted Skills")
    st.write(", ".join(resume_skills) if resume_skills else "No skills detected")

    # Generate embedding for resume
    query_embedding = model.encode([resume_text])[0]

    # Candidate retrieval (get more than needed first, say top 20)
    k_candidates = 20
    D_crs, I_crs = course_index.search(np.array([query_embedding]), k_candidates)

    candidate_courses = [course_metadata[i] for i in I_crs[0]]
    candidate_embeddings = model.encode([c["Course Description"] for c in candidate_courses])

    # Re-rank using MMR for diversity
    mmr_indices = mmr(query_embedding, candidate_embeddings, k=5)
    recommended_courses = [candidate_courses[i] for i in mmr_indices]

    # Display recommendations
    st.subheader("📘 Recommended Courses")
    for course in recommended_courses:
        st.markdown(f"**{course.get('Course Name', 'Untitled')}**")
        st.write(course.get("Course Description", "No description available"))
        st.markdown("---")
