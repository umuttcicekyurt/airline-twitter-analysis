from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import json
import re

# -------------------------------
# Load and clean JSON
# -------------------------------
with open("conversations_with_lufthansa.json", "r", encoding="utf-8") as f:
    nested_data = json.load(f)

tweets_data = [tweet for convo in nested_data for tweet in convo]

def is_valid(tweet):
    return (
        tweet.get("lang") == "en"
        and "text" in tweet
        and not tweet.get("text", "").startswith("RT")
        and len(tweet["text"].split()) > 4
    )

def clean(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\S+", "", text)
    text = re.sub(r"#\S+", "", text)
    return text.strip().lower()

cleaned_texts = [clean(tweet["text"]) for tweet in tweets_data if is_valid(tweet)]

print(f"Using {len(cleaned_texts)} tweets.")

# -------------------------------
# Embedding
# -------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(cleaned_texts, show_progress_bar=True)

# -------------------------------
# KMeans Clustering
# -------------------------------
NUM_TOPICS = 10
kmeans = KMeans(n_clusters=NUM_TOPICS, random_state=42)
labels = kmeans.fit_predict(embeddings)

# -------------------------------
# Display top tweets per cluster
# -------------------------------
from collections import defaultdict

clusters = defaultdict(list)
for label, text in zip(labels, cleaned_texts):
    clusters[label].append(text)

for i in range(NUM_TOPICS):
    print(f"\n=== Topic {i} ===")
    for tweet in clusters[i][:3]:  # top 3 example tweets
        print(f"  {tweet}")
