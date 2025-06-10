import os
import json

input_folder = "cleaned_sent"
output_folder = "cleaned_sent_2"
os.makedirs(output_folder, exist_ok=True)

seen_ids = set()

for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        unique_tweets = []
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            for line in f:
                tweet = json.loads(line)
                tweet_id = tweet.get("id_str")
                if tweet_id is not None and tweet_id not in seen_ids:
                    seen_ids.add(tweet_id)
                    unique_tweets.append(tweet)
        print(f"{filename}: {len(unique_tweets)} unique tweets")  # Debug line
        # Write unique tweets to the output file
        with open(os.path.join(output_folder, filename), 'w', encoding='utf-8') as f_out:
            for tweet in unique_tweets:
                f_out.write(json.dumps(tweet) + "\n")