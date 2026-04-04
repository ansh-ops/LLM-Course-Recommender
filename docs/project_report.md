# Course Matcher Project Report

## 1. Executive Summary

Course Matcher is an AI-powered web application that takes a user's resume as input and recommends relevant courses based on semantic similarity. The app also shows similar profile matches and extracts recognizable skills from the uploaded resume. The current production-facing version uses Flask for the backend, vanilla JavaScript for browser interactions, and a custom HTML/CSS frontend.

The core idea is simple:

1. Read the resume text from a PDF or TXT file.
2. Convert that text into an embedding vector using a sentence transformer model.
3. Search FAISS indexes for similar resumes and relevant courses.
4. Re-rank course candidates using MMR so results are not too repetitive.
5. Return structured JSON to the frontend and render the results in a clean UI.

## 2. Problem Statement

People often have resumes but do not know which courses are the best next step for their skill level and background. Keyword search is too shallow because resumes and course descriptions may express the same idea in different words. This project solves that by using semantic search rather than plain keyword matching.

## 3. Business Value

- Helps users discover relevant upskilling opportunities faster.
- Makes recommendations feel more personalized than normal search.
- Shows both current skill signals and learning gaps.
- Demonstrates a practical AI workflow that combines NLP, search, ranking, and UX.

## 4. High-Level Architecture

### User Flow

1. User opens the web app.
2. User uploads a PDF or TXT resume.
3. Frontend sends the file to `/api/recommend`.
4. Backend extracts text and generates embeddings.
5. Backend searches vector indexes and ranks the results.
6. Backend returns JSON with skills, profile matches, and courses.
7. Frontend renders chips, cards, and links for the results.

### Layers

- Presentation Layer: HTML, CSS, JavaScript
- API Layer: Flask
- AI/NLP Layer: SentenceTransformers embeddings
- Retrieval Layer: FAISS vector search
- Ranking Layer: MMR reranking with cosine similarity
- Data Layer: JSON, pickle, FAISS index files

## 5. Current Tech Stack

### Backend

- Python
- Flask
- NumPy
- FAISS
- SentenceTransformers
- scikit-learn
- PyMuPDF

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript

### Data / Artifacts

- `resume_metadata.json`
- `courses_metadata.pkl`
- `resume_index.faiss`
- `courses_index.faiss`
- `courses.json`

## 6. Easy Explanation Of Each Technology

### Python

Python is the main programming language of the app. It is used because it has strong libraries for AI, NLP, backend APIs, and data processing.

### Flask

Flask is a lightweight web framework. It helps the app expose URLs like `/` and `/api/recommend`. You can think of it as the layer that receives browser requests and sends responses back.

### SentenceTransformers

SentenceTransformers converts text into embeddings. An embedding is a list of numbers that represents meaning. Similar texts produce vectors that are close together in vector space.

### FAISS

FAISS is a vector similarity search library. It stores embeddings and quickly finds which existing items are closest to a new query embedding. That is what makes semantic search fast.

### NumPy

NumPy handles arrays and numeric operations. Embeddings are stored and processed as NumPy arrays before being searched or ranked.

### scikit-learn

scikit-learn is used here for cosine similarity. Cosine similarity measures how aligned two vectors are and helps compare the semantic closeness of embeddings.

### PyMuPDF

PyMuPDF reads text from uploaded PDF resumes. Without it, the backend would not be able to convert a resume PDF into machine-readable text.

### HTML

HTML defines the structure of the frontend page: sections, buttons, cards, text blocks, upload input, and placeholders for results.

### CSS

CSS controls the visual design of the app: layout, colors, fonts, spacing, responsiveness, and the polished card-based interface.

### JavaScript

JavaScript handles frontend interactivity. It listens for the file upload form submit, sends the request to the backend, and renders the returned results dynamically.

### Pickle

Pickle is a Python serialization format. In this app it stores course metadata after preprocessing so the backend can load course details efficiently.

### JSON

JSON is a lightweight data format. It is used for resume metadata storage and API responses.

## 7. Main Files And Their Roles

### `webapp.py`

This is the main backend application.

Responsibilities:

- Initializes the Flask app
- Loads the embedding model
- Loads the FAISS indexes and metadata
- Extracts text from uploaded files
- Extracts skills from resume text
- Searches similar profiles and courses
- Re-ranks courses using MMR
- Exposes the API endpoints

### `templates/index.html`

This is the main page structure.

Responsibilities:

- Defines the upload section
- Defines containers for skills, profile matches, and course recommendations
- Loads CSS and JavaScript assets

### `static/styles.css`

This file contains the custom visual design.

Responsibilities:

- Defines colors and theme variables
- Builds responsive layout
- Styles cards, chips, upload area, status pill, and buttons

### `static/app.js`

This file controls the browser-side behavior.

Responsibilities:

- Handles file selection UI
- Sends uploaded resumes to the backend
- Shows loading and error states
- Renders skills, profiles, and course results dynamically

### `final2.py`

This is the preserved Streamlit-era prototype.

Responsibilities:

- Single-file recommendation prototype
- Demonstrates course recommendation flow
- Uses the same core AI concepts in an older UI

### `resume/resume_mdata.py`

This script builds the resume FAISS index while keeping metadata aligned with vectors.

### `scraper.py`

This script fetches course-like data and writes it to a CSV.

## 8. Functions In `webapp.py`

### `load_model()`

Loads the sentence transformer model. It is cached with `lru_cache` so the model is loaded once and reused.

### `load_resume_data()`

Loads the resume FAISS index and resume metadata.

### `load_course_data()`

Loads the course FAISS index and course metadata.

### `extract_text_from_pdf(file_storage)`

Extracts text from an uploaded PDF file using PyMuPDF.

### `extract_text(file_storage)`

Chooses how to read the uploaded file:

- If PDF: call the PDF extractor
- Else: treat it as UTF-8 text

### `extract_skills_from_resume(resume_text, known_skills)`

Performs basic skill extraction by checking whether known skill keywords appear in the resume text.

### `safe_faiss_search(index, query_embedding, top_k)`

Searches FAISS safely.

Why it matters:

- Clamps `k` so it never asks for more results than exist
- Filters out invalid `-1` ids
- Prevents crashes and bad lookups on small datasets

### `mmr(query_embedding, candidate_embeddings, k=5, lambda_param=0.65)`

Applies Maximal Marginal Relevance.

What it does:

- Chooses results relevant to the query
- Penalizes near-duplicate candidates
- Produces more diverse recommendations

### `build_response(resume_text)`

This is the core application pipeline.

What it does:

1. Loads model and indexes
2. Embeds the resume
3. Extracts skills
4. Finds similar resumes
5. Finds candidate courses
6. Embeds the candidate course descriptions
7. Re-ranks them with MMR
8. Returns the final response structure

### `index()`

Serves the main HTML page at `/`.

### `health()`

Returns a simple health check response at `/api/health`.

### `recommend()`

Main API endpoint at `/api/recommend`.

What it does:

- Validates file upload
- Extracts resume text
- Calls `build_response`
- Returns JSON or error messages

## 9. APIs

### `GET /`

Purpose:

- Serves the main frontend page

Response:

- HTML page

### `GET /api/health`

Purpose:

- Quick health/status endpoint

Example response:

```json
{
  "status": "ok"
}
```

### `POST /api/recommend`

Purpose:

- Accept a resume file and return AI-generated recommendation results

Input:

- Multipart form-data
- Field name: `resume`

Output shape:

```json
{
  "skills": ["Python", "SQL"],
  "profiles": [
    {
      "name": "Alice",
      "summary": "Software engineer skilled in Python, Django, and REST APIs."
    }
  ],
  "courses": [
    {
      "title": "Course Name",
      "university": "Provider Name",
      "description": "Course description text",
      "url": "https://example.com/course",
      "skills": ["Python", "ML"]
    }
  ]
}
```

Error cases:

- Missing file upload
- Unsupported or unreadable file
- Empty extracted text
- Missing FAISS or metadata files
- Runtime errors in recommendation flow

## 10. Data Flow

### Input

- Resume uploaded as PDF or TXT

### Processing

1. Convert resume into text
2. Convert text into embedding
3. Search vector indexes
4. Apply ranking logic
5. Format final JSON

### Output

- Extracted skills
- Similar profiles
- Recommended courses

## 11. Why This Is An AI App

This is an AI app because the app does not rely only on fixed rules or exact keyword matching. It uses a trained language representation model to understand text semantically.

That means:

- It can match related meanings, not just identical words
- It transforms unstructured text into embeddings
- It performs similarity search on those AI-generated vectors
- It ranks and personalizes results from the user's input

In short, the core decision-making layer is based on machine-learned text representations.

## 12. AI Elements Present In The App

### 1. Unstructured Text Understanding

The app accepts free-form resume text rather than rigid form fields.

### 2. Embedding Model

The sentence transformer model converts natural language into vector representations.

### 3. Semantic Search

FAISS retrieves items by vector similarity rather than strict keywords.

### 4. Recommendation Logic

The app recommends learning content based on semantic closeness to user context.

### 5. Ranking And Diversification

MMR balances relevance and diversity to improve recommendation quality.

### 6. Personalized Output

The response changes based on the actual resume content uploaded by the user.

## 13. Current Strengths

- Clear AI pipeline from upload to recommendation
- Uses semantic embeddings instead of basic search
- Fast retrieval with FAISS
- Clean frontend and API separation
- Safer handling for small datasets and invalid FAISS ids
- Simple enough to explain in interviews

## 14. Current Limitations

- Skill extraction is keyword-based rather than model-based
- No authentication or user accounts
- No persistent database
- No evaluation framework for recommendation quality
- Limited resume dataset
- No explanation scoring shown to users yet
- No async/background job model loading optimization

## 15. Future Improvements

- Add course match scores
- Add “why this course” explanations
- Improve skill extraction with NER or LLMs
- Add user history and saved recommendations
- Store data in a database
- Add admin ingestion pipeline for courses
- Add testing around API and ranking behavior
- Add batching, caching, and deployment configuration

## 16. Interview-Friendly Explanation Of The Core Pipeline

If someone asks, “How does your app work?”, a strong short answer is:

“Users upload a resume, the backend extracts the text, turns it into an embedding using SentenceTransformers, and then uses FAISS to find semantically similar resumes and courses. After that, I apply MMR reranking so the final course recommendations are both relevant and diverse. The backend exposes this through a Flask API, and the frontend renders the results dynamically with JavaScript.”

## 17. Interview Questions And Answers Prep

### Architecture And Design

1. What problem does this app solve?
2. Why did you choose a web app architecture instead of a notebook-only prototype?
3. Why did you separate the frontend from the backend?
4. Why is Flask a good fit here?
5. What would change if the app had to support thousands of users?
6. How would you deploy this app in production?
7. How would you store metadata in a more scalable way?
8. How would you version models and indexes?
9. What parts are CPU-heavy?
10. What parts would you cache in production?

### AI / ML / NLP

11. What is an embedding?
12. Why use SentenceTransformers here?
13. What does `all-MiniLM-L6-v2` do?
14. Why is semantic search better than keyword matching in this use case?
15. How do you compare embeddings?
16. What is cosine similarity?
17. What is vector search?
18. Why use FAISS?
19. What is MMR and why did you use it?
20. What are the limitations of embedding-based search?
21. How would you evaluate recommendation quality?
22. How would you reduce hallucination or poor-fit recommendations?
23. How would you improve skill extraction beyond keyword matching?
24. What happens if the resume contains unusual or unseen terms?
25. How would you fine-tune the recommendation system?

### Backend / API

26. Walk me through the `/api/recommend` endpoint.
27. How do you validate uploaded files?
28. How do you handle empty or invalid input?
29. Why did you add `safe_faiss_search`?
30. Why does filtering invalid FAISS ids matter?
31. Why do you use JSON responses?
32. How would you add request logging?
33. How would you add rate limiting?
34. How would you secure file uploads?
35. How would you write automated tests for the API?

### Frontend

36. Why did you move away from Streamlit?
37. How does the frontend communicate with the backend?
38. Why did you use vanilla JavaScript instead of React?
39. How do you handle loading and error states?
40. How does the UI stay responsive on mobile?
41. How would you add progress indicators or animations?
42. How would you improve accessibility?

### Data And Indexing

43. How were the FAISS indexes created?
44. Why must metadata and index rows stay aligned?
45. What happens if you request more FAISS neighbors than exist?
46. What file formats are used and why?
47. How would you update the course index when new courses arrive?
48. How would you handle duplicate or stale course records?

### Debugging And Reliability

49. What bug did you fix in the reranking logic?
50. Why did the MMR bug happen?
51. Why was the `top_k` FAISS usage problematic in the older code?
52. How did you handle NumPy dependency compatibility?
53. What edge cases did you defend against?
54. What monitoring would you add in production?

### Behavioral / Project Ownership

55. What part of this project are you most proud of?
56. What tradeoffs did you make to keep the scope manageable?
57. What would you improve if you had one more week?
58. How would you explain this project to a non-technical stakeholder?
59. What did you learn from turning a prototype into a web app?
60. If this became a startup product, what would your roadmap look like?

## 18. Sample Strong Interview Answers

### Why is this an AI app?

“It is an AI app because the main recommendation logic depends on embeddings generated by a pretrained language model. Instead of exact keyword matches, the system understands semantic similarity between resumes and course descriptions, which makes the recommendations more intelligent and personalized.”

### Why use FAISS?

“FAISS is built for fast nearest-neighbor search over vectors. Since embeddings are high-dimensional vectors, FAISS makes retrieval much faster and more scalable than comparing every course against the query one by one.”

### Why use MMR?

“Raw similarity search often returns very similar courses. MMR helps balance relevance with diversity so the user sees a broader and more useful set of recommendations.”

### What is the most important engineering improvement you made?

“I improved reliability around search and ranking. I added safe FAISS querying to handle small indexes and invalid ids, and I fixed the MMR reranking logic so it does not crash when the candidate pool is smaller than the requested result count.”

## 19. Resume Bullet Ideas Based On This Project

- Built an AI-powered resume-to-course recommendation web app using Flask, SentenceTransformers, FAISS, and custom frontend components.
- Implemented semantic search over resumes and course descriptions using embedding vectors and nearest-neighbor retrieval.
- Improved recommendation quality by adding MMR reranking for more diverse course suggestions.
- Designed and shipped a custom HTML/CSS/JavaScript frontend to replace a Streamlit prototype.
- Hardened the ranking pipeline with safer FAISS query handling, invalid-id filtering, and small-dataset edge case protection.

## 20. Final Takeaway

This project is a strong example of a practical AI application because it combines:

- NLP
- embeddings
- vector databases/search
- recommendation logic
- backend API design
- frontend product design

It is not just a model demo. It is an end-to-end AI product workflow with real input handling, ranking logic, structured responses, and a usable interface.
