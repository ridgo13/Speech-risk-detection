import os
import uuid
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import pandas as pd
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, random_split
import parselmouth
from parselmouth.praat import call
from sqlalchemy import create_engine

# ---------------- CONFIG ----------------
DATA_DIR = r"D:\capstone2\Speech\spectrograms"  
WAV_DIR = r"D:\capstone2\Speech\raw_data"       
BATCH_SIZE = 8  
EPOCHS = 20     
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- DATABASE CONFIG ---
# 1. Fill these in with your GCP details!
DB_HOST = "103.145.155.250"     
DB_PASS = "qz*,2zZQ=4<6v4jY"      
DB_USER = "postgres"
DB_NAME = "speaktrum_db"
DB_PORT = "5432"
# ==========================================
# 1. BIOMARKER EXTRACTION
# ==========================================
def extract_clinical_metrics(wav_path):
    try:
        sound = parselmouth.Sound(wav_path)
        pointProcess = call(sound, "To PointProcess (periodic, cc)", 75, 600)
        jitter = call(pointProcess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        shimmer = call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        hnr = call(call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0), "Get mean", 0, 0)
        return {"jitter": round(jitter*100, 4), "shimmer": round(shimmer*100, 4), "hnr": round(hnr, 2)}
    except:
        return {"jitter": 0.0, "shimmer": 0.0, "hnr": 0.0}

# ==========================================
# 2. ENHANCED DATASET (With Augmentation)
# ==========================================
class ParkinsonHybridDataset(Dataset):
    def __init__(self, img_root, wav_root, is_train=True):
        self.samples = []
        self.categories = [("HC", 0), ("PD", 1)]
        
        if is_train:
            self.transform = transforms.Compose([
                transforms.Grayscale(),
                transforms.Resize((128, 128)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomAffine(degrees=10, translate=(0.1, 0.1)),
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,))
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Grayscale(),
                transforms.Resize((128, 128)),
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,))
            ])

        wav_map = {}
        for root, _, files in os.walk(wav_root):
            for file in files:
                if file.lower().endswith(".wav"):
                    wav_map[os.path.splitext(file)[0].upper().strip()] = os.path.join(root, file)

        for label_name, label in self.categories:
            cat_root = os.path.join(img_root, label_name)
            if not os.path.exists(cat_root): continue
            for root, _, files in os.walk(cat_root):
                for file in files:
                    if file.lower().endswith(".png"):
                        img_id = os.path.splitext(file)[0].upper().replace("MEL_", "").replace("_SPEC", "").strip()
                        if img_id in wav_map:
                            self.samples.append((os.path.join(root, file), wav_map[img_id], label))
                        else:
                            for w_id in wav_map:
                                if img_id in w_id or w_id in img_id:
                                    self.samples.append((os.path.join(root, file), wav_map[w_id], label))
                                    break
        print(f"✅ Sync Complete: {len(self.samples)} pairs.")

    def __len__(self): return len(self.samples)
    def __getitem__(self, idx):
        img_path, wav_path, label = self.samples[idx]
        img = Image.open(img_path).convert('L')
        return self.transform(img), label, wav_path

# ==========================================
# 3. DEEP CNN MODEL
# ==========================================
class DeepRiskClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1))
        )
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(64, 2)
        )

    def forward(self, x):
        return self.classifier(self.features(x).view(x.size(0), -1))

# ==========================================
# 4. TRAINING & DATABASE EXPORT
# ==========================================
if __name__ == "__main__":
    full_dataset = ParkinsonHybridDataset(DATA_DIR, WAV_DIR, is_train=True)
    
    if len(full_dataset) == 0:
        print("🛑 Error: No files found.")
    else:
        train_size = int(0.8 * len(full_dataset))
        train_set, val_set = random_split(full_dataset, [train_size, len(full_dataset)-train_size])
        
        train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=False)

        model = DeepRiskClassifier().to(DEVICE)
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
        criterion = nn.CrossEntropyLoss()

        print(f"🚀 Training for SpeakTrum Risk Detection...")
        for epoch in range(EPOCHS):
            model.train()
            t_loss, t_corr, t_total = 0, 0, 0
            for imgs, labels, _ in train_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                optimizer.zero_grad()
                output = model(imgs)
                loss = criterion(output, labels)
                loss.backward(); optimizer.step()
                
                t_loss += loss.item()
                _, pred = torch.max(output, 1)
                t_total += labels.size(0); t_corr += (pred == labels).sum().item()
            
            scheduler.step()
            print(f"Epoch {epoch+1} -> Loss: {t_loss/len(train_loader):.4f} | Train Acc: {100*t_corr/t_total:.2f}%")

        # --- DATABASE GENERATION & CLOUD UPLOAD ---
        db_entries = []
        model.eval()
        print("\n📊 Pushing results to SpeakTrum database...")
        with torch.no_grad():
            for i in range(len(full_dataset)):
                img, label, wav_path = full_dataset[i]
                output = model(img.unsqueeze(0).to(DEVICE))
                prob_pd = F.softmax(output, dim=1)[0][1].item()
                
                risk = "High" if prob_pd > 0.8 else "Medium" if prob_pd > 0.4 else "Low"
                clinical = extract_clinical_metrics(wav_path)
                db_entries.append({
                    "Patient_UUID": str(uuid.uuid4())[:8],
                    "AI_Assessed_Risk": risk,
                    "Parkinsons_Probability": round(float(prob_pd), 4),
                    "Jitter_Level": clinical["jitter"],
                    "Shimmer_Level": clinical["shimmer"],
                    "HNR_Level": clinical["hnr"],
                    "Audio_Source": os.path.basename(wav_path)
                })

        # Save to Cloud SQL
        try:
            results_df = pd.DataFrame(db_entries)
            engine = create_engine(DB_URL)
            results_df.to_sql('parkinsons_results', engine, if_exists='replace', index=False)
            print("✅ Successfully pushed to 'speaktrum_db'.")
        except Exception as e:
            print(f"❌ Cloud Upload Error: {e}")

        torch.save(model.state_dict(), "parkinsons_high_acc_model.pth")
        print("\n✅ Process Complete.")