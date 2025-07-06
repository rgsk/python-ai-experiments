
import torch
from PIL import Image
from torchvision import models, transforms
from torchvision.datasets import ImageFolder

# CONFIG
IMG_SIZE = 128
MODEL_PATH = "card_classifier.pth"
DATA_DIR = "card_images"  # same directory used during training
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. Load class names

dummy_dataset = ImageFolder(DATA_DIR)
class_names = dummy_dataset.classes

# 2. Define transforms
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor()
])

# 3. Load model
model = models.resnet18(weights=False)
model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model = model.to(device)
model.eval()

# 4. Predict function


def predict_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image_tensor)
        _, predicted = torch.max(output, 1)
        label = class_names[predicted.item()]

    return label


# ✅ Example usage:
predicted_label = predict_image(
    "test/battle-ram.png")
print("Predicted Label:", predicted_label)
