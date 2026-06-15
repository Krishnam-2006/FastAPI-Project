# 📝 [BrewNest]



---

## 🚀 Features

- User registration and login with JWT authentication
- Create, read, update, and delete blog posts
- Profile picture upload (stored locally)
- Server-side rendered pages with Jinja2 templates
- Database migrations with Alembic
- Seed script to populate database with sample data

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | Backend framework |
| PostgreSQL | Database |
| SQLAlchemy (async) | ORM |
| Alembic | Database migrations |
| Jinja2 | HTML templating |
| JWT | Authentication |
| Uvicorn | ASGI server |

---

## ⚙️ Prerequisites

Make sure you have the following installed before starting:

- Python 3.11+
- PostgreSQL
- pip

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone [your-repo-url]
cd [your-project-folder]
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root of your project and fill in the following:

```env
# Database
DATABASE_URL=

# JWT
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=

# Add any other variables your project uses
```

> ⚠️ Never commit your `.env` file to GitHub. Make sure it's listed in `.gitignore`.

---

## 🗄️ Database Setup

**1. Create your PostgreSQL database**
```sql
CREATE DATABASE [your_db_name];
```

**2. Run Alembic migrations to create all tables**
```bash
alembic upgrade head
```

---

## ▶️ Running the App

```bash
uvicorn main:app --reload
```

Then open your browser and go to:
- **App** → http://127.0.0.1:8000
- **API Docs (Swagger)** → http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc)** → http://127.0.0.1:8000/redoc

---

## 🌱 Seeding the Database

To populate the database with sample data run:

```bash
python populate.py
```

This will:
- Clear any existing users, posts, and profile pictures
- Create 5 sample users
- Create 44 sample blog posts distributed across users
- Set realistic post dates automatically

> Note: Make sure the app is running before executing the seed script, as it makes HTTP requests to the API.

---

## 📁 Project Structure

```
[your-project-folder]/
│
├── main.py               # FastAPI app entry point
├── models.py             # SQLAlchemy database models
├── database.py           # Database connection and session
├── populate.py           # Database seed script
├── image_utils.py        # Profile picture utilities
│
├── routers/              # API route handlers
├── templates/            # Jinja2 HTML templates
├── static/               # CSS, JS, static files
├── populate_images/      # Sample images for seeding
├── migrations/           # Alembic migration files
│
├── .env                  # Environment variables (do not commit)
├── .gitignore
└── requirements.txt
```

---

## 📌 Notes

- Profile pictures are stored locally in the filesystem, 
- boto3 is listed as a dependency but S3 integration is not configured in this version
- Based on Fast API learning and using AI this project is made.

---

## 📄 License

[MIT / or whatever license you want — or remove this section]