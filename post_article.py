import os
import json
import sys
import requests

HF_API_KEY = os.getenv("HF_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

TOPIC_FILE = ".blog_topics.json"

def get_next_topic():
    if not os.path.exists(TOPIC_FILE):
        raise Exception("Topic file not found. Ensure generate_topics.py completed successfully.")

    with open(TOPIC_FILE, "r") as f:
        topics = json.load(f)

    if not topics:
        raise Exception("No topics available in topic file.")

    return topics.pop(0), topics

def post_article(topic):
    # Replace this with real article generation and posting logic
    print(f"Posting article on topic: {topic}")
    # Simulate post
    return True

def save_remaining_topics(topics):
    with open(TOPIC_FILE, "w") as f:
        json.dump(topics, f)

def main():
    topic, remaining_topics = get_next_topic()
    success = post_article(topic)

    if success:
        save_remaining_topics(remaining_topics)
        print("Article posted and topics updated.")
    else:
        print("Failed to post article.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
