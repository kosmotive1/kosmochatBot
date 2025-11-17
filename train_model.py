import os
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ------------------- Dataset -------------------
class SimpleTextDataset(Dataset):
    def __init__(self, text_folder, vocab, seq_len=5):
        """
        text_folder: folder containing all .txt documents
        vocab: dictionary mapping words to indices
        seq_len: number of tokens per input sequence
        """
        self.vocab = vocab
        self.seq_len = seq_len

        # Mapping words <-> indices
        self.word2idx = {word: idx for word, idx in vocab.items()}
        self.idx2word = {idx: word for word, idx in vocab.items()}

        # Read all text files
        all_text = ""
        for fname in os.listdir(text_folder):
            if fname.endswith(".txt"):
                with open(os.path.join(text_folder, fname), "r", encoding="utf-8") as f:
                    all_text += f.read().lower() + " "

        tokens = all_text.split()
        self.data = [self.word2idx.get(word, self.word2idx.get("<unk>")) for word in tokens]

    def __len__(self):
        return max(0, len(self.data) - self.seq_len)

    def __getitem__(self, idx):
        seq = self.data[idx:idx + self.seq_len]
        target = self.data[idx + self.seq_len]
        return torch.tensor(seq, dtype=torch.long), torch.tensor(target, dtype=torch.long)

# ------------------- Model -------------------
class KinyaQAModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        emb = self.embedding(x)
        out, _ = self.rnn(emb)
        logits = self.fc(out[:, -1, :])  # predict next token from last hidden state
        return logits

# ------------------- Training -------------------
def train_model(vocab_path, text_folder, save_path="kinyamodel.pth", seq_len=5, epochs=10, batch_size=32, lr=0.005):
    # Load vocab
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    if not vocab:
        print("[ERROR] Vocab is empty!")
        return

    # Prepare dataset and dataloader
    dataset = SimpleTextDataset(text_folder, vocab, seq_len=seq_len)
    if len(dataset) == 0:
        print("[ERROR] Dataset is empty!")
        return

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = KinyaQAModel(len(vocab))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Training loop
    for epoch in range(epochs):
        total_loss = 0
        for x, y in loader:
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

    # Save model
    torch.save(model.state_dict(), save_path)
    print(f"[INFO] Model saved to {save_path}")

# ------------------- Main -------------------
if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    vocab_path = os.path.join(base_dir, "vocab.json")
    documents_folder = os.path.join(base_dir, "documents")  # folder with .txt files
    train_model(vocab_path, documents_folder, seq_len=5, epochs=10, batch_size=32)
