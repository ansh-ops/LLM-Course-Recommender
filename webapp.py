import json
import os
import pickle
from functools import lru_cache

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": os.environ.get("FRONTEND_ORIGIN", "*")}},
)

KNOWN_SKILLS = [
    "Python",
    "SQL",
    "TensorFlow",
    "PyTorch",
    "AWS",
    "Docker",
    "Java",
    "React",
    "NLP",
    "Spark",
    "Hadoop",
    "Tableau",
]


@lru_cache(maxsize=1)
def load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def load_resume_data():
    import faiss

    index = faiss.read_index("resume_index.faiss")
    with open("resume_metadata.json", "r", encoding="utf-8") as file:
        resumes = json.load(file)
    return index, resumes


@lru_cache(maxsize=1)
def load_course_data():
    import faiss

    index = faiss.read_index("courses_index.faiss")
    with open("courses_metadata.pkl", "rb") as file:
        courses = pickle.load(file)
    return index, courses


def extract_text_from_pdf(file_storage):
    import fitz

    document = fitz.open(stream=file_storage.read(), filetype="pdf")
    return " ".join(page.get_text() for page in document)


def extract_text(file_storage):
    content_type = file_storage.mimetype or ""
    filename = (file_storage.filename or "").lower()

    if content_type == "application/pdf" or filename.endswith(".pdf"):
        return extract_text_from_pdf(file_storage)

    return file_storage.read().decode("utf-8", errors="ignore")


def extract_skills_from_resume(resume_text, known_skills):
    resume_text_lower = resume_text.lower()
    return [skill for skill in known_skills if skill.lower() in resume_text_lower]


def safe_faiss_search(index, query_embedding, top_k):
    k = min(top_k, index.ntotal)
    if k == 0:
        return []

    _, indices = index.search(np.asarray([query_embedding], dtype="float32"), k)
    return [int(idx) for idx in indices[0] if idx >= 0]


def cosine_similarity_matrix(a, b):
    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1, keepdims=True)

    a_safe = a / np.clip(a_norm, 1e-12, None)
    b_safe = b / np.clip(b_norm, 1e-12, None)
    return a_safe @ b_safe.T


def mmr(query_embedding, candidate_embeddings, k=5, lambda_param=0.65):
    if len(candidate_embeddings) == 0:
        return []

    selected = []
    candidates = list(range(len(candidate_embeddings)))

    sim_to_query = cosine_similarity_matrix(
        candidate_embeddings, query_embedding.reshape(1, -1)
    ).flatten()
    sim_between_candidates = cosine_similarity_matrix(
        candidate_embeddings, candidate_embeddings
    )

    for _ in range(min(k, len(candidate_embeddings))):
        if not selected:
            idx = int(np.argmax(sim_to_query))
            selected.append(idx)
            candidates.remove(idx)
            continue

        if not candidates:
            break

        mmr_scores = []
        for candidate in candidates:
            sim_to_selected = max(sim_between_candidates[candidate][selected])
            score = lambda_param * sim_to_query[candidate] - (
                1 - lambda_param
            ) * sim_to_selected
            mmr_scores.append(score)

        idx = candidates[int(np.argmax(mmr_scores))]
        selected.append(idx)
        candidates.remove(idx)

    return selected


def build_response(resume_text):
    model = load_model()
    resume_index, resume_metadata = load_resume_data()
    course_index, course_metadata = load_course_data()

    query_embedding = model.encode([resume_text], convert_to_numpy=True)[0]
    detected_skills = extract_skills_from_resume(resume_text, KNOWN_SKILLS)

    resume_indices = safe_faiss_search(resume_index, query_embedding, top_k=4)
    profile_matches = []
    for idx in resume_indices:
        profile = resume_metadata[idx]
        profile_matches.append(
            {
                "name": profile.get("name", "Unknown"),
                "summary": profile.get("text", "No content available"),
            }
        )

    course_indices = safe_faiss_search(course_index, query_embedding, top_k=18)
    candidate_courses = [course_metadata[idx] for idx in course_indices]
    candidate_texts = [
        course.get("Course Description")
        or course.get("Course Name")
        or "No description available"
        for course in candidate_courses
    ]

    candidate_embeddings = (
        model.encode(candidate_texts, convert_to_numpy=True)
        if candidate_texts
        else np.empty((0, query_embedding.shape[0]), dtype="float32")
    )
    ranked_indices = mmr(query_embedding, candidate_embeddings, k=6)

    recommended_courses = []
    for idx in ranked_indices:
        course = candidate_courses[idx]
        recommended_courses.append(
            {
                "title": course.get("Course Name", "Untitled"),
                "university": course.get("University", "Unknown provider"),
                "description": course.get(
                    "Course Description", "No description available"
                ),
                "url": course.get("Course URL", ""),
                "skills": course.get("Skills", []),
            }
        )

    return {
        "skills": detected_skills,
        "profiles": profile_matches,
        "courses": recommended_courses,
    }


@app.get("/")
def index():
    return send_from_directory("public", "index.html")


@app.get("/styles.css")
def styles():
    return send_from_directory("public", "styles.css")


@app.get("/app.js")
def frontend_script():
    return send_from_directory("public", "app.js")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/recommend")
def recommend():
    uploaded_file = request.files.get("resume")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Please upload a PDF or TXT resume."}), 400

    try:
        resume_text = extract_text(uploaded_file).strip()
    except Exception as exc:
        return jsonify({"error": f"Could not read the uploaded file: {exc}"}), 400

    if not resume_text:
        return jsonify({"error": "No readable text was found in that file."}), 400

    try:
        result = build_response(resume_text)
    except FileNotFoundError as exc:
        return jsonify({"error": f"Missing index or metadata file: {exc}"}), 500
    except Exception as exc:
        return jsonify({"error": f"Recommendation failed: {exc}"}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
