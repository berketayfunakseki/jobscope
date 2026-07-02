import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.models import JobListing

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

REMOTEOK_URL = "https://remoteok.com/api"
ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/de/search/1"


def fetch_remoteok_jobs(keyword: str = "python") -> list[dict]:
    """RemoteOK API'sinden ilan cek (anahtar gerekmiyor)."""
    headers = {"User-Agent": "Mozilla/5.0 (jobscope-app)"}
    response = requests.get(REMOTEOK_URL, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    jobs = []
    for item in data:
        if not isinstance(item, dict) or "id" not in item:
            continue
        position = item.get("position", "")
        tags = " ".join(item.get("tags", []))
        if keyword.lower() not in (position + tags).lower():
            continue
        jobs.append({
            "title": position,
            "company": item.get("company", "Unknown"),
            "location": item.get("location", "Remote"),
            "canton": None,
            "source": "remoteok",
            "url": item.get("url", f"https://remoteok.com/remote-jobs/{item['id']}"),
            "description": item.get("description", "")[:2000],
        })
    return jobs


def fetch_adzuna_jobs(keyword: str = "python developer", results: int = 20) -> list[dict]:
    """Adzuna API'sinden Almanya (DE) bolgesinden ilan cek."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": keyword,
        "results_per_page": results,
        "content-type": "application/json",
    }
    response = requests.get(ADZUNA_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    jobs = []
    for item in data.get("results", []):
        jobs.append({
            "title": item.get("title", ""),
            "company": item.get("company", {}).get("display_name", "Unknown"),
            "location": item.get("location", {}).get("display_name", ""),
            "canton": None,
            "source": "adzuna_de",
            "url": item.get("redirect_url", ""),
            "description": (item.get("description") or "")[:2000],
        })
    return jobs


def save_jobs_to_db(jobs: list[dict], db: Session) -> int:
    """Yeni ilanlari veritabanina kaydet, zaten var olanlari atla (url unique)."""
    saved_count = 0
    for job_data in jobs:
        if not job_data.get("url"):
            continue
        existing = db.query(JobListing).filter(JobListing.url == job_data["url"]).first()
        if existing:
            continue
        new_job = JobListing(**job_data)
        db.add(new_job)
        saved_count += 1
    db.commit()
    return saved_count