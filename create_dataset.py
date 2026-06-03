import cv2
import os
from datetime import datetime

# Simple dataset creation tool
# Run this to capture images for your custom dataset

output_dir = "dataset/helmet/train/images"
os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open webcam")
    exit()

print("Dataset creation tool")
print("Press 'c' to capture image")
print("Press 'q' to quit")
print(f"Images will be saved to: {output_dir}")

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Dataset Creator - Press 'c' to capture, 'q' to quit", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"helmet_{timestamp}_{count:03d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)
        print(f"Captured: {filename}")
        count += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Dataset creation complete. Captured {count} images.")
print("Now you need to label these images using a tool like LabelImg:")
print("1. Install LabelImg: pip install labelImg")
print("2. Run: labelImg dataset/helmet/train/images dataset/helmet/classes.txt")
print("3. Label each image and save as YOLO format")
print("4. Move some images to valid/ folder for validation")