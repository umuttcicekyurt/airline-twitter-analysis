import os
import json
import sys

input_folder = os.path.join(os.path.dirname(__file__), "..", "cleaned_sent_2_with_conversation")
target_user_id = "56377143"
output_file = os.path.join(os.path.dirname(__file__), "..", "Conversations_with_all_airlines/conversations_with_KLM.json")

tcount = 0

# Step 1: Group tweets by conversation_root
conversations = {}
for fname in os.listdir(input_folder):
    if fname.endswith(".json"):
        print("Found: " + fname)
        with open(os.path.join(input_folder, fname), "r", encoding="utf-8") as f:
            for line in f:
                tweet = json.loads(line)
                root = tweet["conversation_root"]
                conversations.setdefault(root, []).append(tweet)

print("Loading .json files done")

# Step 2: Find conversations involving the target user
involved_convos = []
for conv in conversations.values():
    if any(tweet["user"]["id_str"] == target_user_id for tweet in conv):
        involved_convos.append(conv)
        tcount = tcount + 1
        print("convo found - " + str(tcount))

print(f"Found {len(involved_convos)} conversations involving user {target_user_id}.")

# Example: Print the tweets in the first such conversation
if involved_convos:
    with open(output_file, "w", encoding="utf-8") as fout:
        json.dump(involved_convos, fout, ensure_ascii=False, indent=2)

print("Done.")
sys.exit(0)