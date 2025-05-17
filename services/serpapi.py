import os
import requests
from dotenv import load_dotenv
load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")


def fetch_serp_news(topic, max_results=5):
    try:
        params = {
         "q": topic,
          "tbm": "nws",
          "api_key": SERP_API_KEY,
           "num": max_results,
          "tbs": "qdr:d"  # ✅ Today only
        }

        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        results = data.get("news_results", [])[:max_results]

        headlines = []
        for result in results:
            title = result.get("title", "").strip()
            snippet = result.get("snippet", "").strip()
            if title and snippet:
                headlines.append(f"{title}: {snippet}")
        return headlines
    except Exception as e:
        print("[ERROR] Failed SERP search:", e)
        return []