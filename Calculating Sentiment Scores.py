import os
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load the model and tokenizer
MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Check if GPU is available and move the model to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
model.to(device)
model.eval()

def batch_xlm_probs(texts, batch_size=16):
    """
    Tokenize & run a batch of texts through the model,
    returning a list of dicts: {"neg": p_neg, "neu": p_neu, "pos": p_pos}
    """
    results = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)  # Move tensors to GPU
        with torch.no_grad():
            logits = model(**batch).logits  
        probs = F.softmax(logits, dim=1) 
        labels = ["neg", "neu", "pos"]
        results.extend([
            {lab: probs[j, k].item() for k, lab in enumerate(labels)}
            for j in range(probs.size(0))
        ])
    return results

# Input and output directories
input_dir = "cleaned"
output_dir = "cleaned_sent"
os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

# Iterate through all files in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith(".json"):  # Process only JSON files
        input_file_path = os.path.join(input_dir, file_name)
        output_file_path = os.path.join(output_dir, file_name)

        # Read and process all tweets in the file
        tweets = []
        texts = []
        with open(input_file_path, encoding="utf-8") as f:
            for line in f:
                tweet = json.loads(line)
                tweets.append(tweet)
                texts.append(tweet.get("text", ""))

        # Get sentiment probabilities for all tweets
        probs_list = batch_xlm_probs(texts)

        # Add sentiment scores to each tweet
        for tweet, probs in zip(tweets, probs_list):
            tweet["sentiment_scores"] = probs

        # Add the maximum sentiment score to each tweet
        for i, tweet in enumerate(tweets):
            if "sentiment_scores" in tweet:
                tweet["sentiment_max"] = max(tweet["sentiment_scores"], key=tweet["sentiment_scores"].get)

        # Save the updated dataset to a new JSON file
        with open(output_file_path, "w", encoding="utf-8") as f:
            for tweet in tweets:
                f.write(json.dumps(tweet) + "\n")
