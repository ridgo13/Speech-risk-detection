

import torch


data = torch.load("cnn_features/sample_0.pt")
print(data["features"].shape)
print(data["label"])
