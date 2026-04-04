import requests
import pandas as pd

# Step 1: Fetch all schools for the given term
schools_url = "https://classes.usc.edu/term-20253/soc/schools.json"
resp = requests.get(schools_url)
data = resp.json()

all_courses = []

print("✅ Found", len(data["schools"]), "schools")

# Step 2: Loop through each school and fetch courses
for school in data["schools"]:
    code = school.get("code")
    name = school["name"]     # e.g. "Computer Science"

    if not code:
        print(f"⚠️ Skipping school without a code: {name}")
        continue

    course_url = f"https://classes.usc.edu/term-20253/soc/{code}.json"

    try:
        r = requests.get(course_url)
        school_data = r.json()
        courses = school_data.get("courses", [])

        print(f"📚 {name} ({code}) - {len(courses)} courses")

        for c in courses:
            all_courses.append({
                "school_code": code,
                "school_name": name,
                "course_number": c.get("course_number"),
                "course_title": c.get("title"),
                "description": c.get("description", ""),
                "units": c.get("units", "")
            })

    except Exception as e:
        print(f"⚠️ Failed to fetch courses for {code}: {e}")

# Step 3: Save everything to CSV
df = pd.DataFrame(all_courses)
df.to_csv("usc_courses.csv", index=False)
print("✅ Saved all courses to usc_courses.csv")
