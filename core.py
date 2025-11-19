# core.py
import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# ---------------- Paths & Constants ---------------- #
PROJECT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
KB_PATH = os.path.join(DATA_DIR, "kb.csv")
EMBEDDINGS_PATH = os.path.join(DATA_DIR, "kb_embeddings.npy")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # small local model
EMBEDDING_SIZE = 384  # model output dim

# Load local sentence-transformers model
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# ---------------- Helper Functions ---------------- #
def ensure_data_dir():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def initialize_kb_if_missing():
    """Create KB file if it doesn't exist"""
    ensure_data_dir()
    if not os.path.isfile(KB_PATH):
        initial_rows = [
            {
                "question": "Imihango isanzwe igira igihe kingana gute?",
                "answer": "Imihango isanzwe imara iminsi 3 kugeza kuri 7. Hagati y'imihango habamo iminsi 21–35.",
                "tags": "imihango,igihe",
            },
            {
                "question": "Ibimenyetso byo gusama ni ibihe?",
                "answer": "Ibimenyetso byo gusama birimo iseseme, kuruka, kunanirwa, amabere ababaza, no gutinda k'ukwezi.",
                "tags": "gusama,pregnancy",
            },
            {
                "question": "Nigute nagabanya kuribwa mu mihango?",
                "answer": "Ushobora kunywa amazi menshi, kuruhuka, gushyushya mu nda, cyangwa gufata imiti igabanya ububabare.",
                "tags": "imihango,ububabare",
            },
        ]
        df = pd.DataFrame(initial_rows)
        df.to_csv(KB_PATH, index=False, encoding="utf-8-sig")

def load_kb() -> pd.DataFrame:
    """Load KB as DataFrame"""
    initialize_kb_if_missing()
    df = pd.read_csv(KB_PATH, encoding="utf-8-sig").fillna("")
    return df[["question", "answer", "tags"]]

def append_kb_entry(question: str, answer: str, tags: str = ""):
    """Add a new question-answer to KB without recomputing embeddings at runtime"""
    df = load_kb()
    new_row = {"question": question.strip(), "answer": answer.strip(), "tags": tags.strip()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(KB_PATH, index=False, encoding="utf-8-sig")
    # ❌ Do NOT call compute_kb_embeddings() here on Render
    # To update embeddings, run `precompute_embeddings.py` locally

# ---------------- Embedding Functions ---------------- #
def embed_text(text: str):
    """Return embedding for a single text using local model"""
    return model.encode(text).tolist()

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def compute_kb_embeddings(df: pd.DataFrame):
    """Compute embeddings for all KB questions and save to file"""
    embeddings = [embed_text(q) for q in df["question"]]
    np.save(EMBEDDINGS_PATH, embeddings)
    return embeddings

def load_kb_embeddings(df: pd.DataFrame):
    """Load cached embeddings or recompute if missing"""
    if os.path.exists(EMBEDDINGS_PATH):
        return np.load(EMBEDDINGS_PATH, allow_pickle=True)
    # If embeddings missing, compute once (memory-heavy)
    return compute_kb_embeddings(df)

# ---------------- Answer Generator ---------------- #
def default_safe_reply():
    return (
        "Ndagusabye imbabazi, sinashoboye gusubiza neza iki kibazo. "
        "Wagishobora kukibaza mu bundi buryo, cyangwa uganire n'umukozi wa KosmoHealth. "
        "Mu bibazo bikomeye by'ubuzima, hamagara +250786305924."
    )

def generate_answer(query: str, df: pd.DataFrame, kb_embeddings=None) -> str:
    """Return best answer for user query using KB embeddings"""
    user_vec = embed_text(query)
    if not user_vec:
        return default_safe_reply()

    if kb_embeddings is None:
        kb_embeddings = load_kb_embeddings(df)

    best_score = -1
    best_idx = -1
    for i, q_vec in enumerate(kb_embeddings):
        score = cosine_similarity(user_vec, q_vec)
        if score > best_score:
            best_score = score
            best_idx = i

    if best_score < 0.4:  # lower threshold for small KB
        return default_safe_reply()

    answer = df.iloc[best_idx]["answer"]
    return (
        f"{answer}\n\n"
        "Icyitonderwa: Ibi ni amakuru rusange. Niba ufite ibibazo bikomeye by'ubuzima, "
        "ganira n'umuganga cyangwa uduhamagara kuri +250786305924."
    )
