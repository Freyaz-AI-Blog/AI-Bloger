import os
import sys
import json
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    print("Error: HF_API_KEY environment variable is not set.")
    sys.exit(1)  # Exit the script early if the API key is missing

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

def query(payload):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Request failed: {response.status_code} {response.reason}")
        print(f"Response content: {response.text}")
        sys.exit(1)

    return response.json()

def generate_topics():
    prompt = "Generate 10 interesting blog topics about AI and machine learning."
    data = query({"inputs": prompt})

    if isinstance(data, list) and "generated_text" in data[0]:
        topics = data[0]["generated_text"].strip().split("\n")
        with open(".blog_topics.json", "w") as f:
            json.dump(topics, f)
        print("Topics saved to .blog_topics.json")
    else:
        print("Unexpected response format:", data)
        sys.exit(1)

if __name__ == "__main__":
    generate_topics()

