tweets = [
    {"created_at": "Wed May 22 12:20:00 +0000 2019", "id_str": "1131172858951024641", "text": "La ruta de easyJet entre Londres y Menorca transporta a m\u00e1s de 19.000 pasajeros en un a\u00f1o https://t.co/Rqy606KVna https://t.co/buWgtqYwCD", "in_reply_to_status_id_str": None, "in_reply_to_user_id_str": None, "user": {"id_str": "393374091", "followers_count": 44323, "friends_count": 845, "statuses_count": 73224, "created_at": "Tue Oct 18 12:55:25 +0000 2011"}, "quote_count": 0, "reply_count": 0, "lang": "es", "favorite_count": 0, "possibly_sensitive": False, "entities": {"hashtags": []}, "sentiment_scores": {"neg": 0.028345301747322083, "neu": 0.7216004133224487, "pos": 0.2500542998313904}, "sentiment_max": "neu"},
    {"created_at": "Wed May 22 12:20:01 +0000 2019", "id_str": "1131172864147808257", "text": "RT @bttr_as1: @goody_tracy Here\u2019s a list of some of @JonesDay clients. They should know Jones Day encouraged McGann to break the law:\n@Macy\u2026", "in_reply_to_status_id_str": None, "in_reply_to_user_id_str": None, "user": {"id_str": "3420691215", "followers_count": 1260, "friends_count": 1468, "statuses_count": 38581, "created_at": "Thu Aug 13 19:18:07 +0000 2015"}, "quote_count": 3, "reply_count": 2, "lang": "en", "favorite_count": 23, "is_retweet": True, "entities": {"hashtags": []}, "sentiment_scores": {"neg": 0.6394182443618774, "neu": 0.31257009506225586, "pos": 0.048011649399995804}, "sentiment_max": "neg"},
    {"created_at": "Wed May 22 12:20:02 +0000 2019", "id_str": "1131172867985485824", "text": "@British_Airways", "in_reply_to_status_id_str": "1131032916232826881", "in_reply_to_user_id_str": "394376606", "user": {"id_str": "394376606", "followers_count": 92, "friends_count": 215, "statuses_count": 385, "created_at": "Thu Oct 20 00:02:49 +0000 2011"}, "quote_count": 0, "reply_count": 0, "lang": "und", "favorite_count": 0, "entities": {"hashtags": []}, "sentiment_scores": {"neg": 0.15329304337501526, "neu": 0.7750301957130432, "pos": 0.07167677581310272}, "sentiment_max": "neu"},
]

LUFTHANSA_ID = "124476322"
total_conversations = 0  # 

for i, tweet_json in enumerate(tweets, 1):
    print(f"\nChecking tweet #{i} with id {tweet_json['id_str']}:")
    if tweet_json["in_reply_to_status_id_str"] is not null:
        if tweet_json["in_reply_to_user_id_str"] == LUFTHANSA_ID:  # Case 1: User is replying to Lufthansa
            if tweet_json["user"]["id_str"] != LUFTHANSA_ID:
                print(f"✅ Conversation: User ({tweet_json['user']['id_str']}) is replying to Lufthansa.")
                total_conversations += 1
            else:
                if tweet_json["reply_count"] > 0:
                    print("✅ Lufthansa replied to itself, and someone replied back, so it's a conversation.")
                    total_conversations += 1
                else:
                    print("❌ Lufthansa replied to itself, and no one responded, so it's not a conversation.")
        else:
            if tweet_json["user"]["id_str"] == LUFTHANSA_ID:  # Case 2: Lufthansa is replying to someone else
                print("✅ Conversation: Lufthansa is replying to someone else")
                total_conversations += 1
            else:
                print(f"❌ Not a conversation: User ({tweet_json['user']['id_str']}) is replying to someone else.")
    else:
        if tweet_json["user"]["id_str"] == LUFTHANSA_ID:
            if tweet_json["reply_count"] > 0:
                print("✅ Conversation: Lufthansa tweeted and has replies.")
                total_conversations += 1
            else:
                print("❌ Not a conversation: Lufthansa tweeted but no replies.")
        else:
            print(f"❌ Not a conversation: User ({tweet_json['user']['id_str']}) tweeted but it's not a reply.")

print(f"\nTotal conversations found: {total_conversations}")