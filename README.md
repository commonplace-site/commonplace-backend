# 🚀 FastAPI Backend - Modular Architecture

This backend project is built using **FastAPI**, designed with a clean and scalable folder structure following best practices for enterprise-grade APIs.

---

## 📁 Folder Structure

app/
├── api/ 
   │ └── v1/ 
          │ └── endpoints/ # API route handlers │ 
            ├── admin.py │ 
            ├── auth.py │ 
            ├── feedback.py │
            ├── notion.py │ 
            ├── scraper.py │ 
            ├── stt.py │ 
            ├── synesthesia.py │
            ├── tts.py │ 
            ├── users.py │ 
            ├── zapier.py 
     │ └── init.py │ 
├── core/ # Configurations and settings 
├── db/ # DB connection and session logic 
├── models/ # SQLAlchemy models 
├── schemas/ # Pydantic schemas 
├── services/ # Business logic and processing 
├── utils/ # Helper and utility functions 
├── main.py # App entrypoint 
├── .env # Environment config (not committed) 
├── alembic.ini # Alembic configuration file 
├── requirements.txt # Project dependencies 
└── .gitignore


---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/commonplace-site/commonplace-backend.git
cd commonplace-backend


2. Create and Activate a Virtual Environment

python -m venv venv
source venv/bin/activate        # For Linux/macOS
venv\Scripts\activate           # For Windows


3. Install Required Packages
pip install -r requirements.txt


To run your FastAPI app locally, use this command:
uvicorn app.main:app --reload




📦 Database Migration (Alembic)
   alembic init alembic

Run Migrations
   alembic upgrade head


🔐 Environment Variables

DATABASE_URL=postgresql://user:password@localhost/db_name
SECRET_KEY=your_secret_key_here
DEBUG=True
