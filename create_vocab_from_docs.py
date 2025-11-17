import os
import re
import json
from collections import Counter

DOCS_FOLDER = "documents"
VOCAB_PATH = "vocab.json"

all_text = ""
for fname in os.listdir(DOCS_FOLDER):
    if fname.endswith(".txt"):
        with open(os.path.join(DOCS_FOLDER, fname), "r", encoding="utf-8") as f:
            all_text += f.read().lower() + " "

tokens = re.findall(r"\w+", all_text)
counter = Counter(tokens)
sorted_words = [word for word, _ in counter.most_common()]

# Build vocab: word -> index
vocab = {"<pad>": 0, "<unk>": 1}
for i, word in enumerate(sorted_words, start=2):
    vocab[word] = i

# Save
with open(VOCAB_PATH, "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

print(f"[INFO] Vocab saved to {VOCAB_PATH}, total words: {len(vocab)}")
