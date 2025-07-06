
import cv2
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


def predict_image(image):
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image_tensor)
        _, predicted = torch.max(output, 1)
        label = class_names[predicted.item()]

    return label


if __name__ == "__main__":

    # ✅ Example usage:
    # predicted_label = predict_image(

    #     Image.open("test/evo-valk.png").convert("RGB")
    # )
    # print("Predicted Label:", predicted_label)

    # Load the image
    img = cv2.imread("public/image-evo-only.png")

    # Crop parameters
    start_x = 41
    width = 238
    height = 450
    x_gap = 40

    # List to hold resized cropped images
    resized_cards = []

    # Extract and resize each card
    for y in [620, 1050]:
        x = start_x
        for i in range(4):
            cropped = img[y:y + height, x:x + width]
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(cropped_rgb)

            resized_cards.append(pil_img)

            x += width + x_gap
    for image in resized_cards:
        predicted_label = predict_image(image)
        print("Predicted Label:", predicted_label)
