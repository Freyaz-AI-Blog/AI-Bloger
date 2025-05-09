import os
import json
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BLOG_DIR = "my_ai_blog"
POSTS_DIR = os.path.join(BLOG_DIR, "_posts")
TOPIC_FILE = ".blog_topics.json"
HF_API_KEY = os.getenv("HF_API_KEY")
GITHUB_REPO = "Freyaz-AI-Blog/AI-Bloger"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def call_huggingface(prompt, max_tokens=700):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
        headers=headers,
        json=payload
    )
    result = response.json()
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return result.get("generated_text", "")

def get_next_topic():
    if not os.path.exists(TOPIC_FILE):
        raise Exception("Topic file not found. Run generate_topics.py first.")

    with open(TOPIC_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    if data["date"] != today:
        raise Exception("Topics are outdated. Run generate_topics.py to refresh.")

    for topic in data["topics"]:
        if topic not in data["used"]:
            data["used"].append(topic)
            with open(TOPIC_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return topic

    print("All topics for today have been used.")
    return None

def generate_article(topic):
    prompt = f"Write a detailed, SEO-optimized blog post about: {topic}. Include an introduction, key points, and a conclusion."
    return call_huggingface(prompt)

def save_article(content, topic):
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}-{topic.replace(' ', '-').replace('/', '').replace('?', '')}.md"
    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: {topic}\n")
        f.write(f"date: {date}\n")
        f.write(f"---\n\n")
        f.write(content)
    return filename

def deploy_to_github():
    os.chdir(BLOG_DIR)
    subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Auto-generated blog post"], check=True)
        subprocess.run(["git", "push", f"https://{ACCESS_TOKEN}@github.com/{GITHUB_REPO}.git", "main"], check=True)
    else:
        print("No changes to commit.")
    os.chdir("..")

def main():
    topic = get_next_topic()
    if topic:
        print(f"Generating article for: {topic}")
        article = generate_article(topic)
        save_article(article, topic)
        deploy_to_github()

if __name__ == "__main__":
    main()
