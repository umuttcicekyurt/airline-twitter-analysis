"""
topic_lufthansa.py  –  zero-shot thread classifier for the LH dataset
---------------------------------------------------------------------
• 8 neutral topics (see LABELS).  Sentiment columns already in JSON
  tell us whether a tweet about that topic is praise or complaint.
• Fast zero-shot (distilbart-mnli-12-3).  Hints with regexes give the
  classifier a nudge when wording is crystal clear.

Outputs  ▸ tweets_classified.csv  (tweet-level rows)
         ▸ console sample of 10 random threads
"""

import re, csv, json, random
from collections import defaultdict
from transformers import pipeline
from tqdm import tqdm
from transformers.pipelines.pt_utils import KeyDataset
import torch


# ─────────────────────────────────────────────────────────────
# 1) EDIT HERE IF YOU CHANGE LABELS
# ─────────────────────────────────────────────────────────────
LABELS = [
    "baggage / luggage issues",
    "flight delay or cancellation",
    "refund or compensation",
    "seat / upgrade issues",
    "app / website issues",
    "contact / reachability",
    "staff service",          # neutral → later split by sentiment
]

THRESH   = 0.6      # absolute score threshold
GAP      = 0.15      # keep other labels within this of top
MAX_KEEP = 3         # never keep more than this

# ─────────────────────────────────────────────────────────────
# 2)  OPTIONAL KEYWORD HINTS  (soft boost, not hard override)
# ─────────────────────────────────────────────────────────────
HINTS = {
    "baggage / luggage issues": [
        re.compile(r"\b(bag|bags|baggage|suitcase|luggage|lost\s+bag|missing\s+bag)\b", re.I)
    ],
    "seat / upgrade issues": [
        re.compile(r"\b(seat|seating|upgrade|seat\s+change|seat\s+map|extra\s+legroom)\b", re.I)
    ],
    "app / website issues": [
        re.compile(r"\b(app|website|site|online\s+check\-?in|login|book(ing)?\s+online|can'?t\s+book)\b", re.I)
    ],
    "contact / reachability": [
        re.compile(r"\b(contact|reach|get in touch|speak to|call|phone|hotline|support|service center|talk to)\b", re.I),
        re.compile(r"\b(no(?:\s+one)?|can't|unable to|trying to|how to|where can I|who can I)\b.{0,30}\b(contact|reach|speak|call|connect)\b", re.I),
    ],
    "staff service": [
        re.compile(
            r"(?i)\b(rude|unhelpful|impolite|arrogant|incompetent|unprofessional)\b"
            r"(?:\W+\w+){0,5}\b(staff|crew|agent|attendant|rep|employee)\b"
        ),
        re.compile(
            r"(?i)\b(staff|crew|agent|attendant|rep|employee)\b"
            r"(?:\W+\w+){0,5}\b(rude|unhelpful|impolite|arrogant|incompetent|unprofessional)\b"
        ),
    ],
}

BOOST = 0.15  



# ─────────────────────────────────────────────────────────────
# 3)  LOAD TWEETS
# ─────────────────────────────────────────────────────────────
with open("conversations_with_AirFrance.json", #CHANGE THIS TO PROPER AIRLINE
          encoding="utf-8") as f:
    nested = json.load(f)

raw = [tw for convo in nested for tw in convo]

def valid(t):
    return (
        "text" in t and
        t.get("lang") in {"en", "de", "es", "fr"} and
        not t["text"].startswith("RT") and
        len(t["text"].split()) > 4
    )

def strip(text:str)->str:
    return re.sub(r"http\S+|@\S+|#\S+", "", text).strip()

threads = defaultdict(list)        # root_id → [cleaned texts]
for tw in raw:
    if not valid(tw):
        continue
    root = tw.get("conversation_root") or tw["id_str"]
    threads[root].append(strip(tw["text"]))

print(f"📦 {len(threads):,} conversation threads loaded")


# ───────────────────────────────────────────────────────────────
# QUICK-TEST SWITCH  ➜  set SAMPLE_THREADS to None for full run
# ───────────────────────────────────────────────────────────────
SAMPLE_THREADS = None         # e.g. 50 threads for a fast test
RANDOM_SAMPLE  = True        # True → pick N at random, False → take first N

if SAMPLE_THREADS is not None:
    all_ids = list(threads.keys())
    keep_ids = (random.sample(all_ids, SAMPLE_THREADS)
                if RANDOM_SAMPLE else all_ids[:SAMPLE_THREADS])

    threads = {tid: threads[tid] for tid in keep_ids}
    print(f"⚡ Quick-test mode: keeping {len(threads)} threads "
          f"out of {len(all_ids)} total")

# 4)  ZERO-SHOT PIPELINE  +  classify() helper
# ─────────────────────────────────────────────
device = 0 if torch.cuda.is_available() else -1

clf = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3",
    multi_label=True,
    device=device
)

print("🖥 Using", "GPU" if device == 0 else "CPU")


BATCH_SZ = 8                # <<— tune up / down to taste

def classify(text: str):
    """
    Classify a single thread.

    • Runs the zero-shot model on the first 1 500 characters.
    • Soft-boosts obvious keyword matches (HINTS + BOOST).
    • Returns a list of (label, score) pairs after THRESH/GAP/MAX_KEEP
      filtering.  Falls back to [('other', 0.0)] when nothing is strong.
    """

    # --- 1) model scores  (now batched ⇒ batch_size really used) ----------
    out = clf(
        [text[:1500]],         # ← wrap in list so batching applies
        LABELS,
        multi_label=True,
        batch_size=BATCH_SZ
    )[0]                       # unpack the single result dict

    best = dict(zip(out["labels"], out["scores"]))

    # --- 2) soft keyword boost --------------------------------------------
        # --- 2) soft keyword boost --------------------------------------------
    lower = text.lower()

    for lbl, regexes in HINTS.items():
        if any(rx.search(lower) for rx in regexes):
            best[lbl] = min(best.get(lbl, 0) + BOOST, 1.0)




    # --- 3) fallback nudge for clear contact questions --------------------------
    if "contact / reachability" not in best:
        if re.search(r"\b(who|how|where).{0,25}(call|contact|reach|get in touch|talk to|speak to)\b", lower):
            best["contact / reachability"] = 0.72  # comfortably over threshold

    # Guard: remove "staff service" if no staff-related complaint
    if "staff service" in best:
        if not any(rx.search(lower) for rx in HINTS["staff service"]):
            best.pop("staff service")

    REFUND_TERMS = re.compile(
    r"\b(refund|compensation|claim|money\s*back|voucher|reimbursement|feedback\s*form|submit.*complaint|waiting\s+for)\b",
    re.I
    )

    if "refund or compensation" in best:
        if not REFUND_TERMS.search(lower):
            best.pop("refund or compensation")


    # --- 3) THRESH / GAP / MAX_KEEP filtering -----------------------------
    ordered = sorted(best.items(), key=lambda x: x[1], reverse=True)

    if not ordered or ordered[0][1] < THRESH:
        return [("other", 0.0)]        # nothing strong enough → “other”

    top_lbl, top_sc = ordered[0]
    keep = [(top_lbl, round(top_sc, 3))]

    for lbl, sc in ordered[1:]:
        if len(keep) >= MAX_KEEP:
            break
        if sc >= THRESH and (top_sc - sc) <= GAP:
            keep.append((lbl, round(sc, 3)))

    return keep


# ─────────────────────────────────────────────────────────────
# 5)  CLASSIFY THREADS + BUILD TWEET-LEVEL ROWS
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# 5)  CLASSIFY THREADS + BUILD TWEET-LEVEL ROWS
# ─────────────────────────────────────────────────────────────
rows = []
for root_id, msgs in tqdm(threads.items(), total=len(threads), desc="Classifying threads"):
    topics = classify(" ".join(msgs))
    primary = topics[0][0] if topics else "other"
    topic_json = json.dumps(dict(topics))  # only includes selected topics

    for tw in (t for t in raw if (t.get("conversation_root") or t["id_str"]) == root_id):
        s = tw.get("sentiment_scores", {})
        sentiments = {
            "neg": s.get("neg", 0),
            "neu": s.get("neu", 0),
            "pos": s.get("pos", 0),
        }
        sentiment_max = max(sentiments, key=sentiments.get)

        text_raw = tw.get("text", "")
        rows.append({
            "id_str":        tw["id_str"],
            "lang":          tw.get("lang", ""),
            "thread_id":     root_id,
            "primary_topic": primary,
            "all_topics":    "|".join(lbl for lbl, _ in topics),
            "topic_scores":  topic_json,

            "sentiment_neg": sentiments["neg"],
            "sentiment_neu": sentiments["neu"],
            "sentiment_pos": sentiments["pos"],
            "sentiment_max": sentiment_max,

            "created_at":    tw.get("created_at", ""),
            "conversation_index": tw.get("conversation_index", ""),
            "text_raw":      text_raw,
        })

print(f"📝 {len(rows):,} tweet-rows ready for CSV")

# ─────────────────────────────────────────────────────────────
# 6)  EXPORT CSV WITH CLEAN COLUMN ORDER
# ─────────────────────────────────────────────────────────────
fieldnames = [
    "id_str", "lang", "thread_id",
    "primary_topic", "all_topics", "topic_scores",
    "sentiment_neg", "sentiment_neu", "sentiment_pos", "sentiment_max",
    "created_at", "conversation_index", "text_raw"
]

with open("tweets_classified_AirFrance.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print("✅ tweets_classified.csv written")


# ─────────────────────────────────────────────────────────────
# 7)  CONSOLE PREVIEW  (remove or comment out in prod)
# ─────────────────────────────────────────────────────────────
PRINT_EXAMPLES = 8

def show_thread(tid, msgs, topics, scores):
    import textwrap, pprint
    bar  = f"─── THREAD {tid} {'─'*25}"
    labs = "|".join(topics)
    scr  = pprint.pformat(scores, compact=True, width=80)
    print(bar);  print(f"🏷 {labs}");  print(f"📊 {scr}");  print("🧵 Full Thread:")
    for i, m in enumerate(msgs):
        wrapped = textwrap.fill(m, 100, subsequent_indent=" "*(len(str(i))+3))
        print(f"[{i}] {wrapped}")
    print()

shown = 0
for tid, msgs in random.sample(list(threads.items()), min(PRINT_EXAMPLES, len(threads))):
    topics_sc = classify(" ".join(msgs))
    show_thread(tid, msgs,
                [l for l, _ in topics_sc],
                {l: s for l, s in topics_sc})
    shown += 1
print(f"(✔) Shown {shown} sample threads")


