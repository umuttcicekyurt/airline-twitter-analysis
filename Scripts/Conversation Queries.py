import os
import json

input_folder = "cleaned_sent_2"
output_folder = "cleaned_sent_2_with_conversation"

os.makedirs(output_folder, exist_ok=True)

# First pass: Build id -> parent_id mapping from all files
id_to_parent = {}
for fname in os.listdir(input_folder):
    if fname.endswith(".json"):
        with open(os.path.join(input_folder, fname), "r", encoding="utf-8") as f:
            for line in f:
                tweet = json.loads(line)
                id_str = tweet["id_str"]
                parent_id = tweet.get("in_reply_to_status_id_str")
                id_to_parent[id_str] = parent_id

# Second pass: For each tweet in each file, add conversation info and write to new file
def find_root_and_index(id_str, id_to_parent, cache):
    path = []
    current = id_str
    while True:
        if current in cache:
            root_id, idx = cache[current]
            for i, tid in enumerate(reversed(path)):
                cache[tid] = (root_id, idx + i + 1)
            return root_id, idx + len(path)
        parent = id_to_parent.get(current)
        if parent is None:
            for i, tid in enumerate(reversed(path)):
                cache[tid] = (current, i + 1)
            cache[current] = (current, 0)
            return current, len(path)
        path.append(current)
        current = parent

cache = {}
for fname in os.listdir(input_folder):
    if fname.endswith(".json"):
        input_path = os.path.join(input_folder, fname)
        output_path = os.path.join(output_folder, fname)
        with open(input_path, "r", encoding="utf-8") as fin, \
             open(output_path, "w", encoding="utf-8") as fout:
            for line in fin:
                tweet = json.loads(line)
                id_str = tweet["id_str"]
                root_id, idx = find_root_and_index(id_str, id_to_parent, cache)
                tweet["conversation_root"] = root_id
                tweet["conversation_index"] = idx
                fout.write(json.dumps(tweet, ensure_ascii=False) + "\n")

