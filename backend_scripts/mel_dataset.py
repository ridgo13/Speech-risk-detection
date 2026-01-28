import os
import numpy as np
import torch
from torch.utils.data import Dataset

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

        # Add channel dimension for CNN
        mel = mel.unsqueeze(0)  # [1, n_mels, time]

        return mel, torch.tensor(label, dtype=torch.long)
