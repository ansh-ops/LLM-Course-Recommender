# Course Matcher

An AI-powered course recommendation system that matches user resumes to similar profiles and relevant online courses using semantic search, vector retrieval, and diversified reranking.

## Features
- Resume upload with PDF and TXT support
- Similar-profile search from a FAISS resume index
- Diverse course recommendations with MMR reranking
- Custom frontend built with Flask, HTML, CSS, and vanilla JavaScript
- Extensible foundation for richer AI explanations and recommendation scoring

## Tech Stack
- Python
- Flask
- SentenceTransformers
- FAISS
- NumPy
- PyMuPDF
- scikit-learn

## Run The Web App
1. Create a virtual environment if you want a clean setup
2. Install dependencies with `pip install -r requirements.txt`
3. If you already have NumPy 2.x in your environment, reinstall with the pinned requirements so `scikit-learn` and `sentence-transformers` stay compatible
4. Make sure `resume_index.faiss`, `courses_index.faiss`, `resume_metadata.json`, and `courses_metadata.pkl` exist in the project root
5. Start the app with `python webapp.py`
6. Open `http://127.0.0.1:5000`

## Deploy On Vercel
- `app.py` is the Vercel Flask entrypoint and imports the Flask `app` from `webapp.py`
- Static assets are served from `public/` for Vercel compatibility
- The FAISS indexes and course metadata pickle are intentionally tracked because the deployed app needs them at runtime

## Main Files
- `webapp.py`: Flask backend and recommendation API
- `app.py`: Vercel-compatible Flask entrypoint
- `templates/index.html`: frontend layout
- `public/styles.css`: custom visual design served by Vercel
- `public/app.js`: upload and results UI served by Vercel
- `final2.py`: preserved Streamlit-era recommendation prototype
- `resume/`: resume index preparation utilities
- `scraper.py`: course data scraping utility
- `docs/project_report.pdf`: generated project report
