import os
import json

input_folder = "combined"
lufthansa_id = "124476322"

# Step 1: Group tweets by conversation_root
conversations = {}
for fname in os.listdir(input_folder):
    if fname.endswith(".json"):
        with open(os.path.join(input_folder, fname), "r", encoding="utf-8") as f:
            for line in f:
                tweet = json.loads(line)
                root = tweet["conversation_root"]
                conversations.setdefault(root, []).append(tweet)

involved_convos = []
for conv in conversations.values():
    # Mentioned if Lufthansa is in user_mentions
    mentioned = any(
        any(
            um.get("id_str") == lufthansa_id
            for um in tweet.get("entities", {}).get("user_mentions", [])
        )
        for tweet in conv
    )
    # Lufthansa did not reply (not the author of any tweet)
    is_author = any(tweet.get("user", {}).get("id_str") == lufthansa_id for tweet in conv)
    if mentioned and not is_author:
        involved_convos.append(conv)

print(f"Found {len(involved_convos)} conversations mentioning Lufthansa but without a reply from them.")

output_file = "conversations_without_lufthansa_reply.json"

with open(output_file, "w", encoding="utf-8") as fout:
    json.dump(involved_convos, fout, ensure_ascii=False, indent=2)

print(f"Saved {len(involved_convos)} conversations to {output_file}.")