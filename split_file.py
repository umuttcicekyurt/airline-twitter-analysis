import os
import json
import math

input_folder = "../data"        
output_folder = "../raw_chunks"  
num_chunks = 4

all_tweets = []

for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        filepath = os.path.join(input_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    tweet = json.loads(line)
                    all_tweets.append(tweet)
                except json.JSONDecodeError:
                    continue  
print(f"Total raw tweets: {len(all_tweets)}")

chunk_size = math.ceil(len(all_tweets) / num_chunks)
os.makedirs(output_folder, exist_ok=True)

for i in range(num_chunks):
    chunk = all_tweets[i * chunk_size : (i + 1) * chunk_size]
    output_path = os.path.join(output_folder, f"raw_chunk_{i + 1}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        for tweet in chunk:
            json.dump(tweet, f)
            f.write("\n")

    print(f"Saved chunk {i + 1} with {len(chunk)} tweets")

