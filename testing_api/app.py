from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from recommendation_model import recommend_top_jobs


app = Flask(__name__)
CORS(app)

# 🔑 Adzuna API credentials
ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"
APP_ID = "API_ID"
APP_KEY = "API_KEY"


@app.route("/")
def home():
    return "✅ Flask backend running"


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """Fetch jobs from Adzuna API"""
    print("✅ /api/jobs route hit!")

    q = request.args.get("q", "")
    location = request.args.get("location", "")
    country = request.args.get("country", "in")
    max_results = int(request.args.get("max_results", 300))

    # Extra params (not used by Adzuna, but you may store for filtering later)
    education = request.args.get("education", "")
    skills = request.args.get("skills", "")
    stipend = request.args.get("stipend", "")
    mode = request.args.get("mode", "")
    duration = request.args.get("duration", "")
    sector = request.args.get("sector", "")
    job_type = request.args.get("job_type", "")

    # Construct Adzuna API URL dynamically with country
    api_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": max_results,
        "what": q or sector,
        "where": location,
    }

    try:
        res = requests.get(api_url, params=params)
        res.raise_for_status()
        data = res.json()

        print(f"✅ {len(data.get('results', []))} jobs fetched successfully")

        return jsonify({
            "success": True,
            "results": data.get("results", []),
            "filters": {
                "education": education,
                "skills": skills,
                "stipend": stipend,
                "mode": mode,
                "duration": duration,
                "sector": sector,
                "job_type": job_type,
            }
        })

    except Exception as e:
        print("❌ Error fetching jobs:", e)
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """Fetch jobs and then generate recommendations"""
    q = request.args.get("q", "")
    location = request.args.get("location", "")
    education = request.args.get("education", "")
    skills = request.args.get("skills", "")
    stipend = request.args.get("stipend", "")
    mode = request.args.get("mode", "")  # full_time / part_time
    duration = request.args.get("duration", "")
    sector = request.args.get("sector", "")
    country = request.args.get("country", "in")
    max_results = int(request.args.get("max_results", 30))

    api_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": max_results,
        "what": q or sector,
        "where": location,
    }

    try:
        res = requests.get(api_url, params=params)
        res.raise_for_status()
        jobs_data = res.json().get("results", [])

        # 🔥 HARD FILTER BY MODE (CRITICAL FIX)
        if mode:
            jobs_data = [
                job for job in jobs_data
                if job.get("contract_time") == mode
            ]

        print(f"✅ Jobs after mode filter ({mode}): {len(jobs_data)}")

        user_profile = {
            "skills": skills,
            "education": education,
            "location": location,
            "stipend": stipend,
            "mode": mode,
            "duration": duration,
            "sector": sector,
        }

        recommended_jobs = recommend_top_jobs(
            user_profile,
            jobs_data,
            top_n=5
        )

        return jsonify({
            "success": True,
            "results": recommended_jobs
        })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)})



if __name__ == "__main__":
    app.run(debug=True)