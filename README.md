# 📝 BrewNest

> A full-stack blog application built with FastAPI, PostgreSQL, and JWT authentication.
> Features server-side rendering with Jinja2, async database operations, and a complete user system.

---

## 🚀 Features

- JWT-based user registration and login with secure password hashing
- Full CRUD operations on blog posts (create, read, update, delete)
- Profile picture upload stored on the server filesystem
- Server-side rendered pages with Jinja2 templates
- Async PostgreSQL integration with SQLAlchemy and Alembic migrations
- Seed script to populate database with 5 users and 44 sample posts

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | Backend framework |
| PostgreSQL | Relational database |
| SQLAlchemy (async) | ORM and query layer |
| Alembic | Database schema migrations |
| Jinja2 | Server-side HTML templating |
| JWT + bcrypt | Authentication and password hashing |
| Uvicorn | ASGI server |

---

## ⚙️ Prerequisites

- Python 3.11+
- PostgreSQL
- pip

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/Krishnam-2006/FastAPI-Project.git
cd FastAPI-Project
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

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/brewnest
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## 🗄️ Database Setup

**1. Create your PostgreSQL database**
```sql
CREATE DATABASE brewnest;
```

**2. Run migrations**
```bash
alembic upgrade head
```

---

## ▶️ Running the App

```bash
uvicorn main:app --reload
```

| URL | Description |
|---|---|
| http://127.0.0.1:8000 | Main app |
| http://127.0.0.1:8000/docs | Swagger UI (API docs) |
| http://127.0.0.1:8000/redoc | ReDoc (alternative docs) |

---

## 🌱 Seeding the Database

```bash
python populate_db.py
```

This creates 5 sample users and 44 blog posts with realistic dates.

> Make sure the app is running before executing — the seed script hits the API directly.

---

## 📁 Project Structure