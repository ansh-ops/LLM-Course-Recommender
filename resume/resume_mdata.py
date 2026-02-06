import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load resume data
with open("resume_metadata.json", "r") as f:
    resumes = json.load(f)

# Ensure 'text' is present in every record
texts = [res["text"] for res in resumes if "text" in res]

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Create FAISS index
dimension = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Save index
faiss.write_index(index, "resume_index.faiss")

# Save metadata separately if not already
with open("resume_metadata.json", "w") as f:
    json.dump(resumes, f)

print("✅ resume_index.faiss successfully created!")
