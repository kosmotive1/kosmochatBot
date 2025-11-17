import os
import re
import json
from collections import Counter

# Folder that contains your text documents
DOCS_FOLDER = os.path.join(os.path.dirname(__file__), "documents")
VOCAB_PATH = os.path.join(os.path.dirname(__file__), "vocab.json")

# Read and combine all text files
all_text = ""
for fname in os.listdir(DOCS_FOLDER):
    if fname.endswith(".txt"):
        file_path = os.path.join(DOCS_FOLDER, fname)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().lower()
            all_text += text + " "
            print(f"[INFO] Loaded {fname}, {len(text.split())} words")

# Tokenize text
tokens = re.findall(r"\w+", all_text)
print(f"[INFO] Found {len(tokens)} total tokens")

# Count word frequencies
counter = Counter(tokens)
sorted_words = [word for word, _ in counter.most_common()]

# Build vocab: word → index mapping
vocab = {"<pad>": 0, "<unk>": 1}
for i, word in enumerate(sorted_words, start=2):
    vocab[word] = i

# Save vocab.json
with open(VOCAB_PATH, "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

print(f"[INFO] Vocab saved to {VOCAB_PATH}")
print(f"[INFO] Total unique words: {len(vocab)}")
