import os
import json
from datetime import datetime
import requests
import re

HF_API_KEY = os.getenv("HF_API_KEY")
print("API key loaded?", bool(HF_API_KEY))  # Optional debug

TOPIC_FILE = ".blog_topics.json"

def call_huggingface(prompt, max_tokens=300):
    if not HF_API_KEY:
        print("HF_API_KEY is not set. Exiting.")
        return ""

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        headers=headers,
        json=payload
    )

    try:
        response.raise_for_status()
        result = response.json()
        print("Raw API response:", result)  # Debug print
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return result.get("generated_text", "")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print(f"Response content: {response.text}")
        return ""
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text was: {response.text}")
        return ""

def generate_topics():
    prompt = (
        "List 10 unique, SEO-friendly blog topics about artificial intelligence. "
        "Each topic should be concise and suitable for a technical blog."
    )
    text = call_huggingface(prompt)
    lines = text.strip().split("\n")
    topics = []
    for line in lines:
        cleaned = re.sub(r"^\d+[\).\s\-]*", "", line).strip()
        if cleaned:
            topics.append(cleaned)
    return topics[:10]

def save_topics(topics):
    today = datetime.now().strftime("%Y-%m-%d")
    data = {"date": today, "topics": topics, "used": []}
    with open(TOPIC_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    topics = generate_topics()
    if topics:
        save_topics(topics)
        print(f"Generated and saved topics for today: {topics}")
    else:
        print("No topics generated. Check logs for details.")

if __name__ == "__main__":
    main()
