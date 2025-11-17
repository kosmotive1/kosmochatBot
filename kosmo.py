import json
import numpy as np
import faiss
import openai
import pickle
import os
 

# -------------------------------
# 1. Set your OpenAI API key
# -------------------------------
openai.api_key = "API_key"  # replace with your key

# -------------------------------
# 2. Load dataset
# -------------------------------
data_file = "training_data.jsonl.txt"
with open(data_file, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

prompts = [entry["prompt"] for entry in data]
completions = [entry["completion"] for entry in data]

# -------------------------------
# 3. Create embeddings for dataset
# -------------------------------
# -------------------------------
# 3. Create embeddings for dataset (with quota handling)
# -------------------------------
embeddings_file = "embeddings.npy"

if os.path.exists(embeddings_file):
    print("Loading existing embeddings...")
    embeddings_np = np.load(embeddings_file)
else:
    print("Creating embeddings...")
    embeddings = []
    for idx, prompt in enumerate(prompts):
        try:
            emb = openai.embeddings.create(
                model="text-embedding-3-small",
                input=prompt
            )['data'][0]['embedding']
            embeddings.append(emb)
        except openai.error.RateLimitError:
            print(f"Quota exceeded at prompt {idx}. Using embeddings created so far.")
            break
        except Exception as e:
            print(f"Error creating embedding for prompt {idx}: {e}")
    if embeddings:
        embeddings_np = np.array(embeddings).astype("float32")
        np.save(embeddings_file, embeddings_np)
    else:
        print("No embeddings could be created. Please check your OpenAI quota.")
        exit(1)


# -------------------------------
# 4. Build or load FAISS index
# -------------------------------
index_file = "faiss_index.index"
dim = embeddings_np.shape[1]

if os.path.exists(index_file):
    print("Loading FAISS index...")
    index = faiss.read_index(index_file)
else:
    print("Creating FAISS index...")
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings_np)
    faiss.write_index(index, index_file)

# -------------------------------
# 5. Save metadata (prompts + completions)
# -------------------------------
meta_file = "meta.pkl"
if not os.path.exists(meta_file):
    with open(meta_file, "wb") as f:
        pickle.dump({"prompts": prompts, "completions": completions}, f)

# -------------------------------
# 6. Function to get relevant context
# -------------------------------
def get_relevant_context(question, top_k=3, distance_threshold=0.5):
    q_emb = openai.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )['data'][0]['embedding']
    
    q_emb_np = np.array([q_emb]).astype("float32")
    distances, indices = index.search(q_emb_np, top_k)
    
    if distances[0][0] > distance_threshold:
        return None
    
    context = "\n".join([completions[i] for i in indices[0]])
    return context

# -------------------------------
# 7. Chatbot function
# -------------------------------
def ask_bot(question):
    context = get_relevant_context(question)
    
    if context is None:
        return "Ndakumva neza, ariko nta makuru mfite ku kibazo cyawe. Waganira n'umuganga w'umwuga."
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Uri umujyanama w'ubuzima bw'abagore, imihango, n'ubuzima bwo gutwita. Sobanura mu Kinyarwanda."},
            {"role": "user", "content": f"Amakuru akurikira agufasha gusubiza:\n{context}\n\nIkibazo: {question}"}
        ]
    )
    
    answer = response['choices'][0]['message']['content']
    return answer

# -------------------------------
# 8. Run chatbot
# -------------------------------
if __name__ == "__main__":
    while True:
        user_question = input("Ikibazo cyawe: ")
        if user_question.lower() in ["exit", "quit"]:
            break
        print("Igisubizo:", ask_bot(user_question))
