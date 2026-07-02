class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    source: str
    url: str
    applied: bool

    class Config:
        from_attributes = True


@app.post("/jobs/fetch")
def fetch_jobs(keyword: str = "python", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    remoteok_jobs = fetch_remoteok_jobs(keyword=keyword)
    adzuna_jobs = fetch_adzuna_jobs(keyword=keyword)

    all_jobs = remoteok_jobs + adzuna_jobs
    saved = save_jobs_to_db(all_jobs, db)

    return {
        "fetched_total": len(all_jobs),
        "new_saved": saved,
        "remoteok_count": len(remoteok_jobs),
        "adzuna_count": len(adzuna_jobs),
    }


@app.get("/jobs", response_model=list[JobOut])
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(JobListing).order_by(JobListing.scraped_at.desc()).all()