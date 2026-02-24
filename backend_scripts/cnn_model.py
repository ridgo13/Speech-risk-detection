<<<<<<< HEAD
import torch
=======
>>>>>>> parishad
import torch.nn as nn

class CNNFeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()

<<<<<<< HEAD
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
=======
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
>>>>>>> parishad
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

<<<<<<< HEAD
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.4)
        self.fc = nn.Linear(32, 2)


    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)

    def extract_features(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
=======
        # Handles variable-length spectrograms
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        self.classifier = nn.Linear(32, 2)

    def forward(self, x):
        x = self.conv_layers(x)
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

    def extract_features(self, x):
        x = self.conv_layers(x)
>>>>>>> parishad
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        return x
