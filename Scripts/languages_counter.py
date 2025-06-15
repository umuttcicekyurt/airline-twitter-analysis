import json
from collections import Counter

# -------------------------------
# Load Lufthansa tweets
# -------------------------------
with open("airline-twitter-analysis/conversations_with_lufthansa.json", "r", encoding="utf-8") as f:
    nested_data = json.load(f)

tweets = [tweet for convo in nested_data for tweet in convo]

# -------------------------------
# Count languages
# -------------------------------
lang_counter = Counter()

for tweet in tweets:
    lang = tweet.get("lang")
    if lang:
        lang_counter[lang] += 1

# -------------------------------
# Show Top 5
# -------------------------------
print("Top 5 Languages:")
for lang, count in lang_counter.most_common(5):
    print(f"{lang}: {count} tweets")
