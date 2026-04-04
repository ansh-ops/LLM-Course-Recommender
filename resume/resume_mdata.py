import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load resume data
with open("resume_metadata.json", "r") as f:
    resumes = json.load(f)

# Keep metadata aligned with the vectors stored in FAISS.
valid_resumes = [res for res in resumes if res.get("text")]
texts = [res["text"] for res in valid_resumes]

if not texts:
    raise ValueError("resume_metadata.json does not contain any resumes with text.")

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Create FAISS index
dimension = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.asarray(embeddings, dtype="float32"))

# Save index
faiss.write_index(index, "resume_index.faiss")

# Save metadata separately if not already
with open("resume_metadata.json", "w") as f:
    json.dump(valid_resumes, f, indent=2)

print("✅ resume_index.faiss successfully created!")
