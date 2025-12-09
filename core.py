import os
import io
from typing import List, Tuple

import pandas as pd
from rapidfuzz import process, fuzz

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KB_PATH = os.path.join(DATA_DIR, "kb.csv")


def ensure_data_dir() -> None:
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def initialize_kb_if_missing() -> None:
    ensure_data_dir()
    if not os.path.isfile(KB_PATH):
        initial_rows = [
            {
                "question": "Imihango isanzwe igira igihe kingana gute?",
                "answer": "Bikunze kumara iminsi 3 kugeza kuri 7, kandi hagati y'imihango habamo iminsi 21–35. Iyo bitandukanye cyane n'ibi, ushobora kugisha inama muganga.",
                "tags": "imihango,igihe",
            },
            {
                "question": "Ibimenyetso byo gusama ni ibihe?",
                "answer": "Ibimenyetso bishobora kuba kuruka cyangwa iseseme, kunanirwa, amabere ababaza, gusinzira cyane, no gutinda k'ukwezi. Kugirango wemeze, ikizamini cya nyababyeyi (pregnancy test) kirafasha.",
                "tags": "gusama,pregnancy",
            },
            {
                "question": "Nigute nagabanya kuribwa mu mihango?",
                "answer": "Gerageza kunywa amazi menshi, kuruhuka, gukora imyitozo yoroshye, gushyushya mu nda (hot water bottle), no gufata imiti igabanya ububabare nko mu byemewe na muganga. Niba biremereye cyane, jya kwa muganga.",
                "tags": "imihango,ububabare",
            },
        ]
        df = pd.DataFrame(initial_rows)
        df.to_csv(KB_PATH, index=False, encoding="utf-8-sig")


def load_kb() -> pd.DataFrame:
    initialize_kb_if_missing()
    try:
        df = pd.read_csv(KB_PATH, encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(KB_PATH)
    for col in ["question", "answer", "tags"]:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    return df[["question", "answer", "tags"]]


def append_kb_entry(question: str, answer: str, tags: str = "") -> None:
    df = load_kb()
    new_row = {"question": question.strip(), "answer": answer.strip(), "tags": tags.strip()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(KB_PATH, index=False, encoding="utf-8-sig")


def search_answers(query: str, df: pd.DataFrame, top_k: int = 3) -> List[Tuple[int, float]]:
    corpus = df["question"].astype(str).tolist()
    results = process.extract(
        query,
        corpus,
        scorer=fuzz.WRatio,
        limit=top_k,
    )
    ranked = [(idx, float(score)) for (_txt, score, idx) in results]
    return ranked


def default_safe_reply() -> str:
    return (
        "Unyihanganire, iki kibazo simbashije kucyumva neza. Gerageza kukibaza mu yandi magambo, "
        "cyangwa uganire n'umuganga uhamagaye kuri +250786305924 cyangwa udusure k'urubuga rwacu rwa KosmoHealth."
    )


def generate_answer(query: str, df: pd.DataFrame) -> str:
    ranked = search_answers(query, df, top_k=3)
    if not ranked:
        return default_safe_reply()

    best_idx, best_score = ranked[0]
    if best_score < 60:
        return default_safe_reply()

    candidate = df.iloc[best_idx]["answer"]
    return (
        f"{candidate}\n\nIcyitonderwa: Ibi ni amakuru rusange. Niba ufite ibibazo bikomeye by'ubuzima, "
        f"ganira n'umuganga cyangwa uduhamagara kuri +250786305924  cyangwa udusure k'urubuga rwacu rwa KosmoHealth."
    )