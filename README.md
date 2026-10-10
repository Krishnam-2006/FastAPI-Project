# BrewNest

![Tests](https://github.com/Krishnam-2006/FastAPI-Project/actions/workflows/tests.yml/badge.svg)

BrewNest is a full-stack blog application built with FastAPI, PostgreSQL and SQLAlchemy (async). It has a REST API, server-rendered pages (Jinja2), user accounts with JWT authentication, database migrations and an automated test suite that runs in GitHub Actions.

## Features

- User registration and login with password hashing and JWT authentication
- Create, read, update and delete blog posts, with pagination
- Authorization: users can only edit or delete their own posts and profile
- Profile picture upload
- Forgot-password and reset-password flow (emails sent through Mailtrap)
- Async SQLAlchemy with PostgreSQL and Alembic migrations
- Server-rendered pages with Jinja2 templates
- Seed script that creates 5 sample users and 44 sample posts
- 59 automated tests, coverage reporting and GitHub Actions CI

## Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | Web framework and REST API |
| PostgreSQL | Database |
| SQLAlchemy (async) | ORM |
| Alembic | Database migrations |
| Jinja2 | HTML templates |
| JWT + password hashing | Authentication |
| Uvicorn | ASGI server |
| pytest, pytest-asyncio, httpx, pytest-cov | Testing and coverage |
| GitHub Actions | Continuous integration |

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Krishnam-2006/FastAPI-Project.git
cd FastAPI-Project
```

### 2. Create a virtual environment

Linux / macOS:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

On Windows, use `copy .env.example .env`.

Open `.env` and fill in your values. `.env.example` lists every variable the app needs, including the Mailtrap mail settings and `FRONTEND_URL`. Never commit your `.env` file.

### 5. Set up the database

Make sure PostgreSQL is running (on Ubuntu or WSL: `sudo service postgresql start`). Then create a user and the development database:

```sql
CREATE USER blog_user WITH PASSWORD 'your_password';
CREATE DATABASE blog OWNER blog_user;
```

Use the same user, password and database name in `DATABASE_URL` in your `.env`:

```env
DATABASE_URL=postgresql+psycopg://blog_user:your_password@localhost:5432/blog
```

Create the tables:

```bash
alembic upgrade head
```

## Running the Application

```bash
uvicorn main:app --reload
```

- Application: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

## Seeding the Database

Start the application first, because the seed script sends requests to the API. Then, in a second terminal with the virtual environment active:

```bash
python populate_db.py
```

## Running the Tests

The tests use a separate PostgreSQL database. Each test starts with empty tables and drops them afterwards, so never point the test database at your real data.

### 1. Create the test database

```sql
CREATE DATABASE blog_test OWNER blog_user;
```

### 2. Set `TEST_DATABASE_URL` in `.env`

```env
TEST_DATABASE_URL=postgresql+psycopg://blog_user:your_password@localhost:5432/blog_test
```

The test setup refuses to run if the database name in this URL does not contain `test`.

### 3. Install the development dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Run the tests

```bash
python -m pytest
```

With a coverage report:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

### Results

- 59 tests passing
- 80% overall coverage
- 100% coverage of `routers/posts.py`

Email sending is mocked in the tests, so no real emails are sent. Profile picture routes and the HTML page routes are not covered yet.

## Continuous Integration

A GitHub Actions workflow (`.github/workflows/tests.yml`) runs on every push and pull request. It starts a PostgreSQL service container with a `blog_test` database, installs `requirements-dev.txt` on Python 3.12 and runs the full pytest suite. The badge at the top of this README shows the latest result.

## What I Added Beyond the Tutorial

This project started from [Corey Schafer's FastAPI tutorial](https://www.youtube.com/watch?v=iukOehU5aF4). On top of it, I added:

- **Test suite:** 59 tests for the user and post routes. They cover registration, login, protected routes, validation errors, pagination, the password reset flow and ownership checks (one user trying to edit or delete another user's data).
- **Isolated test database:** a separate PostgreSQL database that is created and dropped for every test, with a guard that stops the run if its name does not contain `test`.
- **Coverage setup:** pytest-cov with a configuration that measures the async code correctly.
- **Continuous integration:** a GitHub Actions workflow with a PostgreSQL service container.
- **Cross-platform fixes:** the seed script no longer crashes on Linux (it called a Windows-only event loop policy), `requirements.txt` converted from UTF-16 to UTF-8, the missing `httpx` dependency added, and generated profile pictures no longer tracked in Git.
- **Cleanup:** removed a duplicated reset-password route and tidied the application startup and shutdown code.