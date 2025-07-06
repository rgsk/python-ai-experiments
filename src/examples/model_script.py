import json
import os
from io import BytesIO

import requests
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import models
from torchvision.datasets import ImageFolder
from tqdm import tqdm

# CONFIG
DATA_DIR = "card_images"
BATCH_SIZE = 8
EPOCHS = 5
IMG_SIZE = 128
JSONL_FILE = "card_labels_for_script.jsonl"

# 1. Create folders and download images
os.makedirs(DATA_DIR, exist_ok=True)


def download_and_save_images(jsonl_file):
    with open(jsonl_file, 'r') as f:
        for line in tqdm(f, desc="Downloading images"):
            obj = json.loads(line)
            label = obj["label"]
            url = obj["url"]
            label_dir = os.path.join(DATA_DIR, label)
            os.makedirs(label_dir, exist_ok=True)

            filename = os.path.join(label_dir, url.split("/")[-1])
            if not os.path.exists(filename):
                try:
                    response = requests.get(url, timeout=5)
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    img.save(filename)
                except Exception as e:
                    print(f"Failed to download {url}: {e}")


# download_and_save_images(JSONL_FILE)

# 2. Create dataset and dataloaders
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor()
])

dataset = ImageFolder(root=DATA_DIR, transform=transform)
train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# 3. Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, len(dataset.classes))
model = model.to(device)

# 4. Train
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0
    correct = 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()

    acc = 100 * correct / len(dataset)
    print(
        f"Epoch {epoch+1}/{EPOCHS} - Loss: {running_loss:.4f} - Accuracy: {acc:.2f}%")

# Save the model
torch.save(model.state_dict(), "card_classifier.pth")
print("Model saved as card_classifier.pth")
