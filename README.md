# Course Matcher

A resume-driven recommendation app that matches uploaded resumes to similar profiles and relevant online courses using sentence embeddings and FAISS search.

## Features
- Resume upload with PDF and TXT support
- Similar-profile search from a FAISS resume index
- Diverse course recommendations with MMR reranking
- Custom frontend built with Flask, HTML, CSS, and vanilla JavaScript

## Tech Stack
- Python
- Flask
- SentenceTransformers
- FAISS
- NumPy
- PyMuPDF

## Run The Web App
1. Create a virtual environment if you want a clean setup
2. Install dependencies with `pip install -r requirements.txt`
3. If you already have NumPy 2.x in your environment, reinstall with the pinned requirements so `scikit-learn` and `sentence-transformers` stay compatible
4. Make sure `resume_index.faiss`, `courses_index.faiss`, `resume_metadata.json`, and `courses_metadata.pkl` exist in the project root
5. Start the app with `python webapp.py`
6. Open `http://127.0.0.1:5000`

## Main Files
- `webapp.py`: Flask backend and recommendation API
- `templates/index.html`: frontend layout
- `static/styles.css`: custom visual design
- `static/app.js`: upload and results UI
- `final2.py`: preserved Streamlit-era recommendation prototype
