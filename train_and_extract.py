import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# ---------------- CONFIG ----------------
SPECTROGRAM_DIR = "spectrograms"   # contains HC / PD
FEATURE_OUTPUT_DIR = "cnn_features"
BATCH_SIZE = 8
EPOCHS = 5
LEARNING_RATE = 0.001
# --------------------------------------

# ===============================
# DATASET
# ===============================
class MelSpectrogramDataset(Dataset):
    def __init__(self, root_dir):
        self.samples = []

        for label_name, label in [("HC", 0), ("PD", 1)]:
            class_dir = os.path.join(root_dir, label_name)
            for root, _, files in os.walk(class_dir):
                for file in files:
                    if file.endswith(".npy"):
                        self.samples.append(
                            (os.path.join(root, file), label)
                        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]

        mel = np.load(path)
        mel = torch.tensor(mel, dtype=torch.float32)

        # Normalize
        mel = (mel - mel.mean()) / mel.std()

        # Add channel dimension
        mel = mel.unsqueeze(0)  # [1, 128, time]

        return mel, torch.tensor(label, dtype=torch.long)


# ===============================
# COLLATE FUNCTION (PADDING FIX)
# ===============================
def pad_collate(batch):
    mels, labels = zip(*batch)

    max_time = max(mel.shape[-1] for mel in mels)

    padded_mels = []
    for mel in mels:
        pad_amount = max_time - mel.shape[-1]
        padded = F.pad(mel, (0, pad_amount))
        padded_mels.append(padded)

    mels = torch.stack(padded_mels)
    labels = torch.stack(labels)

    return mels, labels


# ===============================
# CNN MODEL
# ===============================
class CNNFeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        # Makes model invariant to time length
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        self.classifier = nn.Linear(32, 2)

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

    def extract_features(self, x):
        x = self.conv_layers(x)
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        return x


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":

    os.makedirs(FEATURE_OUTPUT_DIR, exist_ok=True)

    # Dataset & Loader
    dataset = MelSpectrogramDataset(SPECTROGRAM_DIR)
    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=pad_collate
    )

    print(f"Loaded {len(dataset)} mel-spectrogram samples")

    # Model
    model = CNNFeatureExtractor()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # ===============================
    # TRAINING
    # ===============================
    print("\n🚀 Training CNN...")
    for epoch in range(EPOCHS):
        total_loss = 0.0

        for mel, label in loader:
            optimizer.zero_grad()

            output = model(mel)
            loss = criterion(output, label)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.4f}")

    # ===============================
    # FEATURE EXTRACTION
    # ===============================
    print("\n🧠 Extracting learned features...")
    model.eval()

    with torch.no_grad():
        for idx, (mel, label) in enumerate(loader):
            features = model.extract_features(mel)

            torch.save(
                {
                    "features": features,
                    "label": label
                },
                os.path.join(FEATURE_OUTPUT_DIR, f"sample_{idx}.pt")
            )

    print(f"\n✅ DONE. Learned features saved in '{FEATURE_OUTPUT_DIR}'")
