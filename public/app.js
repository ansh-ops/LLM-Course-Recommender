const form = document.getElementById("upload-form");
const input = document.getElementById("resume-input");
const fileName = document.getElementById("file-name");
const submitButton = document.getElementById("submit-button");
const statusPill = document.getElementById("status-pill");
const skillsContainer = document.getElementById("skills");
const profilesContainer = document.getElementById("profiles");
const coursesContainer = document.getElementById("courses");

input.addEventListener("change", () => {
  const file = input.files[0];
  fileName.textContent = file ? file.name : "No file selected yet";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = input.files[0];
  if (!file) {
    setStatus("Choose a resume file first.", true);
    return;
  }

  const payload = new FormData();
  payload.append("resume", file);

  submitButton.disabled = true;
  setStatus("Analyzing your resume...", false);
  renderLoadingState();

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "The recommendation request failed.");
    }

    renderSkills(data.skills || []);
    renderProfiles(data.profiles || []);
    renderCourses(data.courses || []);
    setStatus("Analysis complete.", false);
  } catch (error) {
    renderErrorState(error.message);
    setStatus(error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

function setStatus(message, isError) {
  statusPill.textContent = message;
  statusPill.classList.toggle("error", isError);
}

function renderLoadingState() {
  skillsContainer.className = "chip-row empty-state";
  profilesContainer.className = "card-stack empty-state";
  coursesContainer.className = "course-grid empty-state";

  skillsContainer.textContent = "Extracting skills...";
  profilesContainer.textContent = "Searching for similar profiles...";
  coursesContainer.textContent = "Ranking course recommendations...";
}

function renderErrorState(message) {
  skillsContainer.className = "chip-row empty-state";
  profilesContainer.className = "card-stack empty-state";
  coursesContainer.className = "course-grid empty-state";

  skillsContainer.textContent = message;
  profilesContainer.textContent = "No profile matches to show.";
  coursesContainer.textContent = "No course recommendations to show.";
}

function renderSkills(skills) {
  skillsContainer.innerHTML = "";
  skillsContainer.className = "chip-row";

  if (!skills.length) {
    skillsContainer.classList.add("empty-state");
    skillsContainer.textContent = "No known skills were detected in the uploaded resume.";
    return;
  }

  skills.forEach((skill) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = skill;
    skillsContainer.appendChild(chip);
  });
}

function renderProfiles(profiles) {
  profilesContainer.innerHTML = "";
  profilesContainer.className = "card-stack";

  if (!profiles.length) {
    profilesContainer.classList.add("empty-state");
    profilesContainer.textContent = "No matching profiles are available.";
    return;
  }

  profiles.forEach((profile) => {
    const card = document.createElement("article");
    card.className = "profile-card";

    const title = document.createElement("h3");
    title.textContent = profile.name;

    const summary = document.createElement("p");
    summary.textContent = profile.summary;

    card.appendChild(title);
    card.appendChild(summary);
    profilesContainer.appendChild(card);
  });
}

function renderCourses(courses) {
  coursesContainer.innerHTML = "";
  coursesContainer.className = "course-grid";

  if (!courses.length) {
    coursesContainer.classList.add("empty-state");
    coursesContainer.textContent = "No recommendations are available yet.";
    return;
  }

  courses.forEach((course) => {
    const card = document.createElement("article");
    card.className = "course-card";

    const provider = document.createElement("div");
    provider.className = "provider";
    provider.textContent = course.university || "Unknown provider";

    const title = document.createElement("h3");
    title.textContent = course.title;

    const description = document.createElement("p");
    description.textContent = course.description;

    card.appendChild(provider);
    card.appendChild(title);
    card.appendChild(description);

    if (Array.isArray(course.skills) && course.skills.length) {
      const skills = document.createElement("div");
      skills.className = "skill-list";

      course.skills.slice(0, 4).forEach((skill) => {
        const pill = document.createElement("span");
        pill.className = "skill-pill";
        pill.textContent = skill;
        skills.appendChild(pill);
      });

      card.appendChild(skills);
    }

    if (course.url) {
      const link = document.createElement("a");
      link.className = "course-link";
      link.href = course.url;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = "Open course";
      card.appendChild(link);
    }

    coursesContainer.appendChild(card);
  });
}
