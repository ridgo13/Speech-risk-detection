# ai/test_inference.py
import torch
from cnn_model import load_model, predict

model = load_model("model.pt")
result = predict("cnn_features/sample_0.pt")

print(result)
