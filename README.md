🧠 Smart Task Analyzer

A productivity tool that intelligently prioritizes tasks using deadlines, importance scores, estimated hours, and dependencies — helping you decide what to work on next.

This project includes:

A Django backend for task processing and scoring

A vanilla HTML/CSS/JS frontend

Deployment-ready setup for Render.com

Ability to add, analyze, and complete tasks in real time

Clean and simple UX suitable for internship/project submissions

🚀 Features
✔ Add Tasks

Each task includes:

Title

Due date (validated to prevent past dates)

Estimated hours

Importance level (1–10)

Optional dependencies

✔ Intelligent Task Analyzer

Your tasks can be sorted using:

Smart Balance Mode

Deadline-Based Sorting

Importance-First Strategy

Quick Tasks First

Also includes:

Circular dependency detection

Priority scoring engine

Top 3 task recommendations

✔ One-Click Task Completion

Completed tasks are removed immediately

Frontend + backend remain in sync

Smart Analyzer updates instantly

✔ Data Persistence

Tasks remain stored even after refreshing the page via:

LocalStorage

Backend syncing

Stateless front-end rendering

🧩 Project Structure
task-analyzer/
│
├── backend/
│   ├── backend/           # Django core configuration
│   ├── tasks/             # Task logic (models, scoring, API)
│   ├── staticfiles/       # Auto-generated during deployment
│   └── manage.py
│
├── frontend/
│   ├── index.html         # Main interface
│   ├── styles.css         # Styling
│   └── script.js          # UI + API communication
│
├── venv/                  # Python virtual environment
├── requirements.txt
├── README.md
└── .gitignore

⚙ Technology Stack
Backend

Python 3.13

Django 5.x

SQLite (for development)

Gunicorn + WhiteNoise (for production)

Frontend

HTML5

CSS3

JavaScript (Vanilla)

Deployment

Render.com Web Service Hosting

Auto collectstatic

Production WSGI using Gunicorn