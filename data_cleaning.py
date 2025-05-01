'''
Cleaning:
-removing the unnecessary attributes
-if important fields are null or cut off then discard (text, the username)
-removing duplicates(no same id)
-removing bots:
--if the time of creation of account is close to the time of the tweet
--no followers/friends
--low num of followers but a lot of tweets
--large following but little likes
-removing non-english tweets
-reject truncated tweets?
'''

import json
from typing import Dict

input_file = "../data/airlines-1558527599826.json"      
output_file = "../cleaned/airlines-1558527599826_cleaned.json" 

keep_fields = ["created_at", "id_str", "text","truncated","in_reply_to_user_id_str" ,"user" , "quoted_status_id_str","quote_count","reply_count","lang"]
keep_user_fields = ["id_str", "followers_count", "friends_count", "statuses_count", "created_at"]
keep_entities_fields = ["hashtags","possibly_sensitive"]

cleaned = []

def valid_tweet(tweet: Dict):
    if "text" not in tweet or tweet['truncated']: #missing text field
        return False
    if "user" not in tweet or "id_str" not in tweet["user"]: #no username or no id of the user
        return False
    '''if "lang" in tweet and tweet["lang"] != "en": #only english tweets
        return False'''
    return True

def keeping_attributes(tweet: Dict):
    cleaned_tweet = {k: tweet[k] for k in keep_fields if k in tweet}

    if "user" in cleaned_tweet:
        cleaned_tweet["user"] = {
            k: tweet["user"][k] for k in keep_user_fields if k in tweet["user"]
            }
    if "entities" in cleaned_tweet:
        cleaned_tweet["entities"] = {
            k: tweet["entities"][k] for k in keep_entities_fields if k in tweet["entities"]
            }
    return cleaned_tweet

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        tweet = json.loads(line)
        if valid_tweet(tweet):
            cleaned_tweet = keeping_attributes(tweet)
            cleaned.append(cleaned_tweet)

with open(output_file, "w", encoding="utf-8") as f:
    for tweet in cleaned:
        json.dump(tweet, f)
        f.write("\n")


print("done cleaning")
