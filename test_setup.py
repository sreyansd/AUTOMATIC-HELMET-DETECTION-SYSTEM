from ultralytics import YOLO
import cv2

# Test YOLO installation
print("Testing YOLO installation...")

try:
    model = YOLO("yolov8n.pt")  # This downloads if not present
    print("✅ YOLO loaded successfully")
except Exception as e:
    print(f"❌ YOLO load failed: {e}")
    exit(1)

# Test OpenCV
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✅ Webcam accessible")
        cap.release()
    else:
        print("❌ Webcam not accessible")
except Exception as e:
    print(f"❌ OpenCV error: {e}")

print("Basic dependencies OK. Now train your helmet model!")