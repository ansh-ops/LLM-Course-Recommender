import faiss
import pickle
import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer
import json


model = SentenceTransformer('all-MiniLM-L6-v2')

with open('courses.json', 'r') as f:
    courses = json.load(f)

course_texts = [c['Course Description'] for c in courses]
embeddings = model.encode(course_texts, show_progress_bar=True)

dimension = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

with open('courses_metadata.pkl', 'wb') as f:
    pickle.dump(courses, f)

faiss.write_index(index, 'courses_index.faiss')

def search_courses(query_text, top_k=5):
    query_embedding = model.encode([query_text])
    D, I = index.search(np.array(query_embedding), top_k)
    return [courses[i] for i in I[0]]

