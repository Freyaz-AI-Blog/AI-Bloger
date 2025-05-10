import os
import sys
import json
import datetime
import re
import subprocess

TOPIC_FILE = ".blog_topics.json"
POSTS_DIR = "posts"

def sanitize_filename(text):
    return re.sub(r'[^a-zA-Z0-9_-]', '', text.replace(' ', '_'))[:50]

def save_article(topic, content):
    os.makedirs(POSTS_DIR, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{POSTS_DIR}/{timestamp}-{sanitize_filename(topic)}.md"
    with open(filename, "w") as f:
        f.write(f"# {topic}\n\n{content}")
    print(f"Article saved to {filename}")
    return filename

def git_commit_file(file_path, message):
    try:
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"Committed and pushed: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed: {e}")
        sys.exit(1)

def main():
    if not os.path.exists(".current_topic.txt") or not os.path.exists(".current_article.txt"):
        print("Missing current article or topic. Exiting.")
        sys.exit(1)

    with open(".current_topic.txt") as f:
        topic = f.read().strip()

    with open(".current_article.txt") as f:
        article = f.read().strip()

    file_path = save_article(topic, article)

    # Remove used topic
    with open(TOPIC_FILE, "r") as f:
        topics = json.load(f)

    remaining_topics = topics[1:]  # pop first

    with open(TOPIC_FILE, "w") as f:
        json.dump(remaining_topics, f)

    git_commit_file(file_path, f"feat: post article on {topic}")
    git_commit_file(TOPIC_FILE, "chore: update remaining topics")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
