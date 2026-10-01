# AI StudyBuddy — Team 5

**Module:** AI-Augmented Backend Development – A&S  
**Team Leader:** Narmadha A  
**Team:** Navaneetha V, Neya Sri P, Nithiya Shree, Nivetha P

## Features in this starter project
- Student registration and login (passwords are hashed)
- SQLite database for users and saved study notes
- Add and delete study notes
- Offline extractive text summarizer
- Fill-in-the-blank quiz generator
- Study assistant guidance page
- Responsive dashboard UI

> Important: This is a runnable educational starter project, not the original team's existing GitHub repository. The summary and quiz use simple offline text processing, and the assistant is a placeholder response—not a connected generative AI model. Connect an approved AI provider/API to add real LLM functionality.

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract this ZIP and open the `AI_StudyBuddy_Team5` folder in VS Code.
3. Open Terminal in that folder.
4. Run:
   ```bash
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.
6. Register an account and log in.

The SQLite database `studybuddy.db` is created automatically when you start the app.

## Main routes
- `/register` — create account
- `/login` — sign in
- `/dashboard` — dashboard and saved notes
- `/notes` — save study notes
- `/summary` — summarize pasted text
- `/quiz` — generate practice questions
- `/chat` — study assistant page

For a real deployment, set a strong `SECRET_KEY`, disable Flask debug mode, add CSRF protection, validate uploads, and integrate a properly secured AI API key via environment variables.
