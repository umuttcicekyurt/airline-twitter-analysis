import json
import os
from typing import Dict
from datetime import datetime

input_dir = "data"
output_dir = "cleaned"
os.makedirs(output_dir, exist_ok=True) 

keep_fields = ["created_at", "id_str", "text","in_reply_to_status_id_str", "in_reply_to_user_id_str", "user", "quoted_status_id_str", "quote_count", "reply_count", "lang", "favorite_count", "retweeted_count", "possibly_sensitive", "is_retweet","possible_bot"]
keep_user_fields = ["id_str", "followers_count", "friends_count", "statuses_count", "created_at"]
keep_entities_fields = ["hashtags"]

def valid_tweet(tweet: Dict) -> bool:
    """Check if the tweet is valid."""
    return "text" in tweet and "user" in tweet and "id_str" in tweet["user"]

def is_bot(user: Dict, tweet_created_at: str) -> bool:
    """Check if a user is likely a bot."""
    followers = user.get("followers_count", 0)
    friends = user.get("friends_count", 0)
  
    if followers == 0 or friends == 0:
        return True

    return False

def extract_fields(source: Dict, fields: list) -> Dict:
    """Extract specified fields from a source dictionary."""
    return {field: source.get(field, 0) for field in fields}

def keeping_attributes(tweet: Dict) -> Dict:
    """Clean and keep only the required attributes of a tweet."""
    if "extended_tweet" in tweet and "full_text" in tweet["extended_tweet"]:
        tweet["text"] = tweet["extended_tweet"]["full_text"]

    if "retweeted_status" in tweet:
        tweet["is_retweet"] = True

    if is_bot(tweet.get("user", {}), tweet.get("created_at", "")):
        tweet["possible_bot"] = True

    for key in ("retweeted_status", "quoted_status"):
        if key in tweet:
            tweet.update(extract_fields(tweet[key], ["reply_count", "retweet_count", "favorite_count", "quote_count"]))

    for nested in ("retweeted_status", "quoted_status", "quoted_status_permalink"):
        tweet.pop(nested, None)

    cleaned = {k: tweet[k] for k in keep_fields if k in tweet}

    if "user" in cleaned:
        cleaned["user"] = {k: tweet["user"][k] for k in keep_user_fields if k in tweet["user"]}

    if "entities" in tweet:
        cleaned["entities"] = {k: tweet["entities"][k] for k in keep_entities_fields if k in tweet["entities"]}

    return cleaned

def process_file(input_path: str, output_path: str):
    """Process a single file and clean tweets."""
    cleaned = []
    seen_ids = set() 
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                
                try:
                    tweet = json.loads(line)
                    if valid_tweet(tweet):
                        if tweet["id_str"] not in seen_ids:
                            seen_ids.add(tweet["id_str"])
                            cleaned.append(keeping_attributes(tweet))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line {i} in {input_path}: {e}")

        with open(output_path, "w", encoding="utf-8") as s:
            for tweet in cleaned:
                json.dump(tweet, s)
                s.write("\n")
    except Exception as e:
        print(f"Error processing file {input_path}: {e}")

for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".json", "_cleaned.json"))
        process_file(input_path, output_path)

print("done cleaning")