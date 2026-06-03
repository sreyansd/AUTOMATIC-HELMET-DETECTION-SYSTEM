import os
import zipfile
from pathlib import Path

# Replace this with a direct Roboflow dataset download link if you have one.
# If you do not have a direct link, this script will still create the folder
# structure and print the manual instructions.
DATASET_URL = os.environ.get(
    "ROBOFLOW_HELMET_DATASET_URL",
    "https://universe.roboflow.com/ds/your-dataset-link-here",
)
DATASET_ZIP = "helmet_dataset.zip"

DATASET_DIR = Path("dataset/helmet")


def create_dataset_structure():
    (DATASET_DIR / "train" / "images").mkdir(parents=True, exist_ok=True)
    (DATASET_DIR / "train" / "labels").mkdir(parents=True, exist_ok=True)
    (DATASET_DIR / "valid" / "images").mkdir(parents=True, exist_ok=True)
    (DATASET_DIR / "valid" / "labels").mkdir(parents=True, exist_ok=True)


def download_dataset():
    create_dataset_structure()
    print("Dataset folder structure created at dataset/helmet/")

    if DATASET_URL == "https://universe.roboflow.com/ds/your-dataset-link-here":
        print("No direct download URL configured.")
        print("To use this script you can either set the ROBOFLOW_HELMET_DATASET_URL environment variable")
        print("or manually download the dataset from Roboflow and extract it into dataset/helmet/.")
        print("Manual steps:")
        print("  1. Visit: https://universe.roboflow.com/yolo-project-0sfck/helmet-detection-ligfk")
        print("  2. Click 'Download Dataset'")
        print("  3. Select 'YOLOv8' format")
        print("  4. Extract the ZIP into dataset/helmet/")
        print("  5. Verify images/labels exist under dataset/helmet/train and dataset/helmet/valid")
        return

    print("Downloading dataset from Roboflow...")
    try:
        import requests

        response = requests.get(DATASET_URL, stream=True)
        response.raise_for_status()
        with open(DATASET_ZIP, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        with zipfile.ZipFile(DATASET_ZIP, "r") as zip_ref:
            zip_ref.extractall(DATASET_DIR)
        os.remove(DATASET_ZIP)
        print("Dataset downloaded and extracted to dataset/helmet/")
    except Exception as exc:
        print(f"Dataset download failed: {exc}")
        print("Please download manually from Roboflow and extract to dataset/helmet/")


if __name__ == "__main__":
    download_dataset()
