import os
import json

input_folder = "cleaned_sent_2_with_conversation"
target_user_id = "124476322"

# Step 1: Group tweets by conversation_root
conversations = {}
for fname in os.listdir(input_folder):
    if fname.endswith(".json"):
        with open(os.path.join(input_folder, fname), "r", encoding="utf-8") as f:
            for line in f:
                tweet = json.loads(line)
                root = tweet["conversation_root"]
                conversations.setdefault(root, []).append(tweet)

# Step 2: Find conversations involving the target user
involved_convos = []
for conv in conversations.values():
    if any(tweet["user"]["id_str"] == target_user_id for tweet in conv):
        involved_convos.append(conv)

print(f"Found {len(involved_convos)} conversations involving user {target_user_id}.")

# Example: Print the tweets in the first such conversation
if involved_convos:
    for tweet in sorted(involved_convos[0], key=lambda t: t["conversation_index"]):
        print(f"{tweet['user']['id_str']} ({tweet['conversation_index']}): {tweet['text']}")