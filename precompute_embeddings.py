from core import load_kb, compute_kb_embeddings

# Load your KB
df = load_kb()

# Compute embeddings and save to file
compute_kb_embeddings(df)

print("✅ KB embeddings computed and saved to 'data/kb_embeddings.npy'")
