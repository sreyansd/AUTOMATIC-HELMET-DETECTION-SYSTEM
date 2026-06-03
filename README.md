# Real-Time Helmet + License Plate Detection System

This project detects helmets on motorcyclists in real-time video and reads license plates when helmets are not worn.

## Project Structure
```
AUTOMATIC HELMET DETECTION Project/
├── Models/
│   ├── helmet_plate_detection.py    # Main detection script
│   ├── helmet_best.pt              # Trained helmet detection model
│   └── plate_best.pt               # Trained plate detection model (optional)
├── dataset/
│   └── helmet/
│       ├── train/
│       │   ├── images/             # Training images
│       │   └── labels/             # YOLO format labels
│       ├── valid/
│       │   ├── images/             # Validation images
│       │   └── labels/             # YOLO format labels
│       ├── classes.txt             # Class names for labeling
│       └── data.yaml               # Dataset configuration
├── output/                         # Generated logs and violation images
├── train_helmet.py                 # Model training script
├── create_dataset.py               # Dataset creation tool
├── download_dataset.py             # Dataset download helper
├── test_setup.py                   # Test dependencies
└── README.md
```

## Quick Start

### 1. Install Dependencies
```bash
pip install opencv-python numpy ultralytics pytesseract labelImg
```

### 2. Get a Helmet Detection Model

#### Option A: Download Pre-trained Model (Recommended)
1. Go to [Roboflow Universe](https://universe.roboflow.com/search?q=helmet+detection)
2. Find a helmet detection dataset (e.g., "Helmet Detection" by yolo-project-0sfck)
3. Download in YOLOv8 format
4. Extract to `dataset/helmet/` folder
5. Run training: `python train_helmet.py`

#### Option B: Create Your Own Dataset
1. Run: `python create_dataset.py`
2. Press 'c' to capture images of people with/without helmets
3. Install LabelImg: `pip install labelImg`
4. Label images: `labelImg dataset/helmet/train/images dataset/helmet/classes.txt`
5. Run training: `python train_helmet.py`

### 3. Test the System
```bash
python Models/helmet_plate_detection.py
```

## How It Works

1. **Helmet Detection**: Uses YOLOv8 to detect if rider is wearing helmet
2. **Plate Detection**: If no helmet, detects and reads license plate
3. **OCR**: Uses Tesseract to extract text from license plate
4. **Logging**: Saves violation records and images

## Output

- **Live Video**: Shows detection results with bounding boxes
- **Console**: Status messages
- **Files**:
  - `output/violations.csv`: Log of all violations
  - `output/no_helmet/`: Images of violations

## Training Your Own Model

### Dataset Format
- Images: `.jpg` or `.png` files
- Labels: `.txt` files with YOLO format (class_id x_center y_center width height)
- Classes: `helmet`, `no-helmet`

### Training Command
```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.train(data="dataset/helmet/data.yaml", epochs=50, imgsz=640)
```

## Troubleshooting

### Model Loading Errors
- Ensure `helmet_best.pt` exists and is not corrupted
- Check file size (>100MB for trained models)

### Webcam Issues
- Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` if camera index is different

### OCR Issues
- Install Tesseract: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Verify path in script matches your installation

## Requirements

- Python 3.8+
- Webcam
- Tesseract OCR
- GPU recommended for training

## License

This project is for educational purposes. Ensure compliance with local laws regarding surveillance and data collection.