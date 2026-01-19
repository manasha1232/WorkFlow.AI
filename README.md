###WorkFlow.AI — Backend

An AI-powered backend system that automates email-driven productivity using secure Google OAuth authentication and scheduled background processing.

⸻

📌 Project Overview

WorkFlow.AI Backend is a FastAPI-based server that securely connects to a user’s Google account and automates email-related productivity tasks such as email processing, task extraction, scheduling, and spam handling.

The backend is designed to:
	•	Authenticate users using Google OAuth 2.0
	•	Create and manage user-specific data
	•	Periodically process emails using a background scheduler
	•	Provide clean REST APIs for frontend consumption
	•	Ensure privacy, security, and user isolation

This repository contains backend code only.

⸻

🎯 What This Project Does (

🔹 Problem

Users receive large volumes of emails that contain:
	•	Tasks
	•	Meetings
	•	Deadlines
	•	Spam

Manually identifying and acting on these emails is inefficient and error-prone.

⸻


The backend system:
	1.	Authenticates users securely using Google OAuth
	2.	Identifies users uniquely by their Google email
	3.	Automatically processes emails at scheduled intervals
	4.	Extracts useful information like:
	•	Tasks
	•	Calendar events
	•	Email summaries
	•	Spam indicators
	5.	Stores and serves user-specific data through APIs

Each user’s data is fully isolated, meaning:
	•	No user can access another user’s emails or tasks
	•	All processing is done per user

⸻

🔐 Authentication Flow (Google OAuth)
	1.	User clicks “Continue with Google” on frontend
	2.	Backend redirects user to Google OAuth consent screen
	3.	Google returns an authorization code
	4.	Backend exchanges code for access token
	5.	Backend retrieves user email
	6.	Backend:
	•	Creates a new user if first login
	•	Retrieves existing user if already registered
	7.	User is redirected back to frontend dashboard

✔ No passwords are stored
✔ Secure and industry-standard authentication

⸻

🧩 Backend Features

✅ User Management
	•	Create user on first login
	•	Reuse user on subsequent logins
	•	User-based data isolation

✅ Email Processing
	•	Read email metadata (with permission)
	•	Categorize emails
	•	Prepare data for summarization and task creation

✅ Task & Calendar Handling
	•	Extract tasks from emails
	•	Prepare calendar events
	•	Store results per user

✅ Scheduler
	•	Runs in background
	•	Periodically checks emails
	•	Can be started/stopped globally

✅ REST API Design
	•	Clean, modular route structure
	•	Easy frontend integration
	•	Scalable for future AI enhancements

⸻

🏗️ Tech Stack

Component	Technology
Backend Framework	FastAPI
Authentication	Google OAuth 2.0
Database	SQLAlchemy
Scheduler	Background Scheduler
API Style	REST
Environment Config	python-dotenv
Language	Python


⸻

📁 Folder Structure (Backend Only)

workflow_ai_backend/
│
├── main.py                # FastAPI app entry point
├── routes/                # All API routes
│   ├── auth.py            # Google OAuth login & callback
│   ├── user.py            # User-related APIs
│   ├── email.py
│   ├── email_read.py
│   ├── email_process.py
│   ├── email_scheduler.py
│   ├── email_history.py
│   ├── email_summarize.py
│   ├── email_spam_filter.py
│   ├── tasks.py
│   ├── calendar.py
│   ├── drive.py
│   └── docs.py
│
├── db/
│   ├── database.py        # DB connection
│   ├── models.py          # DB models
│   ├── crud.py            # DB operations
│   └── init_db.py         # Table creation
│
├── scheduler/
│   └── scheduler.py       # Background scheduler
│
├── utils/
│   └── oauth.py           # OAuth helper logic
│
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation


⸻

🔑 Environment Variables (.env)

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
FRONTEND_URL=http://localhost:5173

⚠️ .env must NOT be committed to GitHub.

⸻

▶️ How to Run the Backend

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn main:app --reload

Backend runs at:

http://localhost:8000


⸻

🧪 Example API Endpoints

Endpoint	Description
/api/auth/login	Start Google OAuth
/api/auth/callback	OAuth callback
/api/user/me	Get current user
/api/email/process	Process emails
/api/email/history	Email history
/api/tasks	User tasks
/api/calendar	Calendar data


⸻

🔒 Security & Privacy
	•	OAuth-based authentication
	•	No password storage
	•	Token-based access
	•	User data isolation
	•	Explicit Google permissions

⸻

🚀 Future Enhancements

	•	Notification system
	•	Role-based access
	•	Production HTTPS deployment

⸻

📜 License

This project is developed for academic and educational purposes.

