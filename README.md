# Smart Parking Management System

This project detects available roadside parking spaces using a **single image** (monocular view) captured from a side perspective. It uses **object detection**, and **geometry-based reasoning** to identify gaps between vehicles and estimate whether a given car type can fit into those gaps.

---

## 🚗 Key Features

- **YOLO-based Object Detection** to identify and locate cars in the input image.
- **Car Type-Aware Slot Estimation**: Computes required space based on the incoming car type (Hatchback, Sedan, SUV, or Truck).
- **Dynamic Scaling** using real-world average car length ratios to estimate pixel widths accurately.
- **Visual Debug Tools** to show bounding boxes, gaps, and detected available spaces.

---

## 🔧 Technologies Used

- Python
- OpenCV
- PyTorch
- YOLOv5 / YOLOv8 (for car detection)
- NumPy

---

## 📐 Vehicle Types and Average Lengths

| Type      | Avg Length (m) |
|-----------|----------------|
| Hatchback | 3.9            |
| Sedan     | 4.2 (reference)|
| SUV       | 4.8            |
| Truck     | 6.0            |

These are used to calculate the relative pixel width of an incoming car, based on a detected reference car in the image.

---

## 🧠 How It Works

1. **Input**:
    - A roadside image with visible parked cars.
    - The incoming car type (e.g., `"SUV"`).

2. **Car Detection**:
    - YOLO detects all cars and provides bounding boxes and types.

3. **Reference Scaling**:
    - The first detected car acts as a **reference vehicle**.
    - Width of incoming car type is estimated using real-world length ratios.

4. **Gap Detection**:
    - Detects all horizontal gaps between adjacent vehicles in the image.

5. **Slot Estimation**:
    - For each gap, calculates how many cars of the incoming type can fit with a safety gap.
    - Outputs bounding boxes for valid parking slots.

6. **Visualization (Optional)**:
    - Display image with boxes for detected cars and estimated parking slots.

---

## 🖼️ Sample Workflow

```python
from smart_parking_system import SmartParkingSystem

detector = SmartParkingSystem(input_image_path, incoming_car_type)
detector.run()
detector.visualize()
```
## 📁 Directory Structure
```bash
.
├── smart_parking_system.py       # Main class with detection and estimation logic
├── test_cases/
│   └── images.jpg       # Test Case Images
├── yolov8n.pt            # Object Detection Model
└── README.md
└── app.py
```

## ⚙️ Setup and Usage Instructions
1. Clone the Repository

```.bash
git clone https://github.com/varshath-akula/SmartParkingManagementSystem.git
cd SmartParkingManagementSystem
```
2. Install Dependencies
```.bash
pip install -r Requirements.txt
```
3. Run the Streamlit App
```.bash
streamlit run app.py
```
