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

## Split Deployment

### Frontend on Vercel
- Vercel now deploys the static frontend only
- `vercel.json` builds `dist/` from `public/`
- Set the Vercel environment variable `COURSE_MATCHER_API_BASE_URL` to your backend API URL, for example `https://your-render-service.onrender.com`

### Backend API on Render
- Render runs the Flask API using `render.yaml`
- The backend still uses `app.py` and `webapp.py`
- Set the Render environment variable `FRONTEND_ORIGIN` to your Vercel domain, for example `https://llm-course-recommender.vercel.app`
- Keep `courses_index.faiss`, `courses_metadata.pkl`, `resume_index.faiss`, and `resume_metadata.json` in the repo because the backend needs them at runtime
- The Render start command must bind to Render's port: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1`

## Main Files
- `webapp.py`: Flask backend and recommendation API
- `app.py`: Flask app entrypoint for API deployment
- `public/index.html`: static frontend page
- `public/styles.css`: custom visual design
- `public/app.js`: upload and results UI
- `public/config.js`: runtime frontend API configuration fallback
- `scripts/build_frontend.py`: writes the Vercel-ready static build
- `vercel.json`: Vercel static deployment config
- `render.yaml`: Render backend deployment config
- `final2.py`: preserved Streamlit-era recommendation prototype
- `resume/`: resume index preparation utilities
- `scraper.py`: course data scraping utility
- `docs/project_report.pdf`: generated project report
