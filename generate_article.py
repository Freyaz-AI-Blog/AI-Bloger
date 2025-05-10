import os
import sys
import json
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    print("Error: HF_API_KEY environment variable is not set.")
    sys.exit(1)

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

def query(prompt):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit(1)

    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    else:
        print("Unexpected response format:", data)
        sys.exit(1)

def generate_article(topic):
    prompt = f"Write a detailed, engaging blog post about: {topic}"
    return query(prompt)

if __name__ == "__main__":
    topic_file = ".blog_topics.json"

    if not os.path.exists(topic_file):
        print("Topic file not found.")
        sys.exit(1)

    with open(topic_file, "r") as f:
        topics = json.load(f)

    if not topics:
        print("No topics left.")
        sys.exit(0)

    topic = topics.pop(0)  # take the first topic and remove it

    article = generate_article(topic)

    with open(".current_topic.txt", "w") as f:
        f.write(topic)

    with open(".current_article.txt", "w") as f:
        f.write(article)

    with open(topic_file, "w") as f:
        json.dump(topics, f, indent=2)  # update topic file

    print("Article generated and saved.")
