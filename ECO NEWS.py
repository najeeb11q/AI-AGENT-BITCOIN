
from dotenv import load_dotenv
import os

# Specify the full path to the .env file
load_dotenv(dotenv_path="C:/Users/NAJEEB AHMED/PycharmProjects/open cv python/.env")

# Debugging: Print all environment variables to see if they are loaded
print("Environment variables:", os.environ)

# Get the values of SUPABASE_URL and SUPABASE_KEY
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Debugging: Print the values of SUPABASE_URL and SUPABASE_KEY
print(f"Supabase URL: {supabase_url}")
print(f"Supabase Key: {supabase_key}")

# Initialize the Supabase client only if the URL and key are valid
if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL or Key not found in environment variables!")

from supabase import create_client
supabase = create_client(supabase_url, supabase_key)



import os
from openai import OpenAI
from supabase import create_client, Client
import requests
from datetime import datetime

# Environment Variables


# Initialize Clients
client = OpenAI(api_key=OPENAI_API_KEY)


def newsapi_finance_news(category: str = "macro"):
    from datetime import datetime, timedelta

    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    queries = {
        "macro": "economy global market trends",
        "bitcoin": "cryptocurrency bitcoin finance"
    }

    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": NEWSAPI_KEY,
        "q": queries.get(category, "finance"),
        "language": "en",
        "sortBy": "publishedAt",
        "from": from_date,
        "pageSize": 5
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        news_data = response.json().get('articles', [])

        return [
            {
                "title": article.get('title', '')[:255],  # Limit title length
                "url": article.get('url', '')[:500],  # Limit URL length
                "description": article.get('description', '')[:1000]  # Limit description
            }
            for article in news_data
        ]
    except requests.RequestException as e:
        print(f"NewsAPI Error: {e}")
        return []


def store_news_in_supabase(news_items):
    current_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    data_to_insert = [
        {
            "timestamp": current_timestamp,
            "finance_info": f"Title: {item['title']}\nURL: {item['url']}\nDescription: {item['description']}"
        }
        for item in news_items
    ]

    try:
        result = supabase.table('econews').insert(data_to_insert).execute()
        return result.data
    except Exception as e:
        print(f"Supabase Insertion Error: {e}")
        return []


def finance_news_tool(finance_category: str = "macro"):
    news_results = newsapi_finance_news(finance_category)

    if not news_results:
        return {"status": "failed", "message": "No news found"}

    stored_news = store_news_in_supabase(news_results)

    return {
        "status": "success",
        "news_count": len(stored_news),
        "stored_news": stored_news
    }


# Optional: SQL to create correct table schema in Supabase
CREATE_TABLE_SQL = """
CREATE TABLE econews (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    finance_info TEXT
);
"""

if __name__ == "__main__":
    result = finance_news_tool()
    print(result)