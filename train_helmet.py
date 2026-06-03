import os
from ultralytics import YOLO

# Dataset configuration for helmet detection
data_yaml = """
train: train/images
val: valid/images

nc: 2
names: ['helmet', 'no-helmet']
"""

# Create dataset directory structure
os.makedirs("dataset/helmet/train/images", exist_ok=True)
os.makedirs("dataset/helmet/train/labels", exist_ok=True)
os.makedirs("dataset/helmet/valid/images", exist_ok=True)
os.makedirs("dataset/helmet/valid/labels", exist_ok=True)

# Save data.yaml
with open("dataset/helmet/data.yaml", "w") as f:
    f.write(data_yaml.strip())

print("Dataset structure created.")
print("Now you need to:")
print("1. Download helmet detection dataset from Roboflow or Kaggle")
print("2. Place images in dataset/helmet/train/images and dataset/helmet/valid/images")
print("3. Place YOLO format labels (.txt) in dataset/helmet/train/labels and dataset/helmet/valid/labels")
print("4. Run this script again to train the model")

# Check if dataset exists
train_images = os.listdir("dataset/helmet/train/images") if os.path.exists("dataset/helmet/train/images") else []
val_images = os.listdir("dataset/helmet/valid/images") if os.path.exists("dataset/helmet/valid/images") else []

if len(train_images) > 0 and len(val_images) > 0:
    print(f"Found {len(train_images)} training images and {len(val_images)} validation images.")
    print("Starting training...")

    model = YOLO("yolov8n.pt")
    model.train(data="dataset/helmet/data.yaml", epochs=50, imgsz=640, project="Models", name="helmet_training")

    # Copy the best model
    import shutil
    if os.path.exists("Models/helmet_training/weights/best.pt"):
        shutil.copy("Models/helmet_training/weights/best.pt", "Models/helmet_best.pt")
        print("Training complete! Model saved as Models/helmet_best.pt")
    else:
        print("Training completed but best.pt not found. Check the training output.")
else:
    print("No dataset found. Please add images and labels first.")