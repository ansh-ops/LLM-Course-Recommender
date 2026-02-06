import json

sample_resumes = [
    {"name": "Alice", "text": "Software engineer skilled in Python, Django, and REST APIs."},
    {"name": "Bob", "text": "Data analyst with experience in SQL, Tableau, and Excel."},
    {"name": "Charlie", "text": "Machine learning engineer with PyTorch and computer vision background."},
    {"name": "Dana", "text": "Frontend developer with React, HTML, CSS, and JavaScript skills."},
    {"name": "Eli", "text": "Cloud architect with AWS, Docker, and Kubernetes experience."}
]

with open("resume_metadata.json", "w") as f:
    json.dump(sample_resumes, f)
