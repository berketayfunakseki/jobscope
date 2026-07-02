from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Berke'nin hedef profili - CV'deki beceri ve rol tanimlariyla hizali
CANDIDATE_PROFILE = """
Data Analytics Machine Learning Backend Development Python FastAPI SQL
scikit-learn Docker PostgreSQL REST API Power BI Pandas NumPy Git CI/CD
software engineer developer intern junior data scientist ML engineer
"""


def score_job(job_title: str, job_description: str) -> float:
    """
    Bir is ilanini aday profiline gore 0-100 arasi puanla.
    TF-IDF + cosine similarity kullanir.
    """
    job_text = f"{job_title} {job_description or ''}"

    documents = [CANDIDATE_PROFILE, job_text]
    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        # bos/anlamsiz metin gelirse
        return 0.0

    return round(similarity * 100, 2)


def score_all_jobs(jobs: list) -> list:
    """JobListing objeleri listesini skorla, skora gore azalan sirala."""
    scored = []
    for job in jobs:
        score = score_job(job.title, job.description)
        job.score = score
        scored.append(job)

    scored.sort(key=lambda j: j.score or 0, reverse=True)
    return scored