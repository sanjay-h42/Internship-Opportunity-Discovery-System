import re
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

OUTPUT_FILE = "recommendations.txt"


def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_similarity(user_text, job_texts):
    corpus = [user_text] + job_texts
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )
    tfidf = vectorizer.fit_transform(corpus)
    return cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()


def clear_old_recommendations():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")


def save_recommendations(user_profile, ranked_jobs):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"Recommendation Run: {datetime.now()}\n")
        f.write(f"User Profile: {user_profile}\n\n")

        for idx, job in enumerate(ranked_jobs, 1):
            f.write(f"{idx}. {job.get('title')}\n")
            f.write(f"   Company: {job.get('company', {}).get('display_name')}\n")
            f.write(f"   Location: {job.get('location', {}).get('display_name')}\n")
            f.write(f"   Salary: {job.get('salary_min')} - {job.get('salary_max')}\n")
            f.write(f"   URL: {job.get('redirect_url')}\n\n")


def recommend_top_jobs(user_profile, jobs, top_n=5):
    if not jobs:
        return []

    user_text = clean_text(
        f"{user_profile.get('skills', '')} {user_profile.get('education', '')}"
    )

    job_texts = [
        clean_text(job.get("title", "") + " " + job.get("description", ""))
        for job in jobs
    ]

    similarity_scores = compute_similarity(user_text, job_texts)
    if np.all(similarity_scores == 0):
        fallback_jobs = jobs[:top_n]
        clear_old_recommendations()
        save_recommendations(user_profile, fallback_jobs)
        return fallback_jobs
    final_scores = []
    for idx, job in enumerate(jobs):
        score = similarity_scores[idx]

        # 📍 Location boost
        if user_profile.get("location"):
            loc = job.get("location", {}).get("display_name", "")
            if user_profile["location"].lower() in loc.lower():
                score += 0.2

        # 🕒 Mode boost (FIXED FIELD)
        if user_profile.get("mode") and job.get("contract_time"):
            if user_profile["mode"] == job["contract_time"]:
                score += 0.15

        # 💰 Stipend boost
        try:
            stipend = float(user_profile.get("stipend", 0))
            if job.get("salary_min") and job.get("salary_max"):
                if job["salary_min"] <= stipend <= job["salary_max"]:
                    score += 0.1
        except:
            pass

        final_scores.append(score)

    top_indices = np.argsort(final_scores)[::-1][:top_n]
    ranked_jobs = [jobs[i] for i in top_indices]

    clear_old_recommendations()
    save_recommendations(user_profile, ranked_jobs)

    return ranked_jobs

