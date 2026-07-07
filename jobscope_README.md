# Jobscope — Swiss / EU Job Market Tracker

A FastAPI backend that aggregates live job listings from multiple sources, deduplicates them, and scores each posting against a candidate profile using TF-IDF cosine similarity. Built to solve my own job search — tracking junior Data/ML/Backend roles across Switzerland and the EU.

## What it does

- Pulls live listings from the **RemoteOK** and **Adzuna** APIs
- Deduplicates postings by normalising the URL (strips query strings) before storing
- Scores every job 0–100 against a candidate profile via **TF-IDF + cosine similarity** (scikit-learn)
- Exposes everything through a **JWT-authenticated REST API**
- Persists to SQLite by default (swappable for Postgres via `DATABASE_URL`)

## Tech stack

FastAPI · SQLAlchemy · scikit-learn · python-jose (JWT) · passlib (bcrypt) · Docker

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Create a new user |
| POST | `/token` | Log in, get a JWT access token |
| GET | `/me` | Current authenticated user |
| POST | `/jobs/fetch?keyword=` | Fetch + save new listings from RemoteOK and Adzuna |
| GET | `/jobs` | List all stored listings |
| POST | `/jobs/score` | Score all listings against the candidate profile, return top 5 |

## Running locally

```bash
pip install -r requirements.txt

# Adzuna needs free API credentials — https://developer.adzuna.com
# create a .env file:
echo "ADZUNA_APP_ID=your_id" >> .env
echo "ADZUNA_APP_KEY=your_key" >> .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env

uvicorn src.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Running with Docker

```bash
docker build -t jobscope .
docker run -p 8000:8000 --env-file .env jobscope
```

## Why these choices

- **FastAPI over Flask** — native async support for concurrent calls to two external APIs without blocking, plus free request validation via Pydantic.
- **SQLite by default** — the workload is read-heavy with batch writes; no need for a dedicated Postgres container at this scale. `DATABASE_URL` swaps it out when needed.
- **TF-IDF over embeddings** — job postings are keyword-dense. A sparse vector representation gets comparable ranking quality with zero external API dependency and zero inference cost.

## What I'd improve next

- Scheduled fetch via cron instead of manual trigger
- Response caching on `/jobs/score`
- More job sources beyond RemoteOK/Adzuna

---
Berke Tayfun Akseki — [berketayfunakseki.com](https://berketayfunakseki.com)
