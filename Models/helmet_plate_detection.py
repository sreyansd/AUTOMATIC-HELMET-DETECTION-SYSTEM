import os
import sys
import csv
import glob
import cv2
from datetime import datetime
from ultralytics import YOLO
import pytesseract

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from database.database import insert_violation
    from database.challan import generate_challan
    DB_AVAILABLE = True
except Exception:
    insert_violation = None
    generate_challan = None
    DB_AVAILABLE = False

# Configure Tesseract path from environment or default Windows install path
TESSERACT_CMD = os.environ.get(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

MODEL_DIR = os.path.join(ROOT_DIR, "Models")
helmet_model_path = os.path.join(MODEL_DIR, "helmet_best.pt")
plate_model_path = os.path.join(MODEL_DIR, "plate_best.pt")

if not os.path.exists(helmet_model_path):
    fallback_path = os.path.join(ROOT_DIR, "yolov8n.pt")
    if os.path.exists(fallback_path):
        print(f"Warning: Helmet model not found at {helmet_model_path}. Using {fallback_path} for testing.")
        helmet_model_path = fallback_path
    else:
        raise FileNotFoundError(
            "Helmet model not found. Place Models/helmet_best.pt or root yolov8n.pt in the project."
        )

print(f"Loading helmet model from: {helmet_model_path}")
helmet_model = YOLO(helmet_model_path)

if os.path.exists(plate_model_path):
    try:
        plate_model = YOLO(plate_model_path)
        plate_model_available = True
    except Exception as exc:
        print(f"Warning: Could not load plate model: {exc}")
        plate_model = None
        plate_model_available = False
else:
    print(f"Warning: Plate model not found at {plate_model_path}. Plate detection will be skipped.")
    plate_model = None
    plate_model_available = False

OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
NO_HELMET_DIR = os.path.join(OUTPUT_DIR, "no_helmet")
CHALLAN_DIR = os.path.join(OUTPUT_DIR, "challans")
PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed_images")
LOG_PATH = os.path.join(OUTPUT_DIR, "violations.csv")

for path in (NO_HELMET_DIR, CHALLAN_DIR, PROCESSED_DIR):
    os.makedirs(path, exist_ok=True)

if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "helmet_status",
            "plate_text",
            "image_path",
            "challan_path",
        ])

CLASS_NAMES = ["helmet", "no-helmet"]


def detect(frame):
    helmet_results = helmet_model(frame)[0]
    plate_results = plate_model(frame)[0] if plate_model_available else None
    return helmet_results, plate_results


def has_helmet(result):
    for box in result.boxes:
        if int(box.cls[0]) == 0:
            return True
    return False


def read_plate(plate_img):
    if plate_img is None or plate_img.size == 0:
        return ""
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(
        binary,
        config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    return text.strip()


def draw_detection_boxes(frame, result, default_label, color):
    for box in result.boxes:
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
        cls_id = int(box.cls[0]) if box.cls is not None else None
        label = default_label
        if cls_id is not None and cls_id < len(CLASS_NAMES):
            label = CLASS_NAMES[cls_id]
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def save_violation(frame, plate_text, fine_amount=500):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = f"no_helmet_{timestamp}.jpg"
    image_path = os.path.join(NO_HELMET_DIR, image_name)
    cv2.imwrite(image_path, frame)

    challan_name = f"challan_{timestamp}.pdf"
    challan_path = os.path.join(CHALLAN_DIR, challan_name)
    if generate_challan is not None:
        generate_challan(plate_text or "UNKNOWN", "No helmet", fine_amount, challan_path)
    else:
        challan_path = ""

    relative_image_path = os.path.join("no_helmet", image_name).replace("\\", "/")
    relative_challan_path = os.path.join("challans", challan_name).replace("\\", "/") if challan_path else ""

    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            "no_helmet",
            plate_text,
            relative_image_path,
            relative_challan_path,
        ])

    if DB_AVAILABLE and insert_violation is not None:
        try:
            insert_violation(
                vehicle_number=plate_text,
                violation_type="No Helmet",
                fine_amount=fine_amount,
                date_time=datetime.now(),
                image_path=relative_image_path,
                challan_pdf=relative_challan_path,
                status="UNPAID",
            )
        except Exception as exc:
            print(f"Warning: could not save violation to database: {exc}")


def annotate_frame(frame, helmet_det, plate_det):
    label_text = "Helmet detected: OK" if has_helmet(helmet_det) else "NO HELMET"
    color = (0, 255, 0) if has_helmet(helmet_det) else (0, 0, 255)
    cv2.putText(frame, label_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    if not has_helmet(helmet_det):
        plate_text = ""
        if plate_det is not None and plate_det.boxes:
            box = plate_det.boxes[0]
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
            plate_roi = frame[y1:y2, x1:x2]
            plate_text = read_plate(plate_roi)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(
                frame,
                f"Plate: {plate_text}",
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )
        save_violation(frame, plate_text)

    draw_detection_boxes(frame, helmet_det, "helmet", (0, 255, 0))
    if plate_det is not None:
        draw_detection_boxes(frame, plate_det, "plate", (255, 255, 0))


def process_image_folder(limit=5):
    image_folder = os.path.join(ROOT_DIR, "dataset", "helmet", "valid", "images")
    image_paths = glob.glob(os.path.join(image_folder, "*.jpg")) + glob.glob(os.path.join(image_folder, "*.png"))
    if not image_paths:
        print(f"No validation images found in {image_folder}.")
        return

    for i, image_path in enumerate(image_paths[:limit]):
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Could not load image: {image_path}")
            continue

        helmet_det, plate_det = detect(frame)
        annotate_frame(frame, helmet_det, plate_det)

        output_path = os.path.join(PROCESSED_DIR, f"processed_{i}.jpg")
        cv2.imwrite(output_path, frame)
        print(f"Processed image saved to: {output_path}")

    print("Processing complete. Check the output/processed_images folder for results.")


def process_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam. If you want to process images, add valid images to dataset/helmet/valid/images.")
        return

    print("Webcam started. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        helmet_det, plate_det = detect(frame)
        annotate_frame(frame, helmet_det, plate_det)

        cv2.imshow("Helmet Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    image_files = glob.glob(os.path.join(ROOT_DIR, "dataset", "helmet", "valid", "images", "*.jpg")) + glob.glob(
        os.path.join(ROOT_DIR, "dataset", "helmet", "valid", "images", "*.png")
    )

    if image_files:
        process_image_folder(limit=len(image_files))
    else:
        process_webcam()
