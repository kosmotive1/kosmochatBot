# local_model_class.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class KinyaQAModel(nn.Module):
    """
    Kinyarwanda Q&A model.
    """

    def __init__(self, vocab_size=10000, hidden_size=256, output_size=None):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.output_size = output_size or vocab_size

        self.embedding = nn.Embedding(self.vocab_size, self.hidden_size)
        self.fc1 = nn.Linear(self.hidden_size, self.hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, x):
        """
        Forward pass.
        """
        x = self.embedding(x)
        if x.dim() == 3:
            x = x.mean(dim=1)  # simple mean pooling if needed
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

    def tokenizer(self, text):
        """
        Convert string to token indices safely.
        """
        if isinstance(text, str):
            return [ord(c) % self.vocab_size for c in text]
        elif isinstance(text, (list, tuple)):
            return text
        elif isinstance(text, torch.Tensor):
            return text
        else:
            raise ValueError("Input must be str, list, tuple, or Tensor")

    def predict(self, text, vocab_mapping, tokenizer=None, device="cpu"):
        """
        Generate readable output from the model using vocab_mapping.
        """
        x = tokenizer(text) if tokenizer else self.tokenizer(text)

        if not isinstance(x, torch.Tensor):
            x = torch.tensor([x], dtype=torch.long, device=device)
        else:
            x = x.to(device)

        self.to(device)
        self.eval()

        with torch.no_grad():
            out = self.forward(x)

        # Convert tensor to token indices
        if out.dim() == 2:
            tokens = out.argmax(dim=-1).squeeze().tolist()
            if isinstance(tokens, int):
                tokens = [tokens]
        elif out.dim() == 3:
            tokens = out.argmax(dim=-1).squeeze().tolist()
            if isinstance(tokens, int):
                tokens = [tokens]
        else:
            tokens = [int(out.item())]

        # Map tokens to words
        words = [vocab_mapping.get(idx, "<unk>") for idx in tokens]
        return " ".join(words)
