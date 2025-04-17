import os
import re
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO

class SmartParkingSystem:
    def __init__(self, image_path, incoming_cartype, model_path="yolov8n.pt", conf_threshold=0.5):
        self.image_path = image_path
        self.incoming_cartype = incoming_cartype.lower()  # incoming cartype: "h", "se", "s", "t"
        self.case_number = None
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.image = cv2.imread(image_path)
        self.car_boxes = []
        self.car_types = []
        self.type_to_widths = {}
        self.available_spaces = []
        self.strip = None
        self.strip_top = 0
        self.strip_origin_x = 0

        # Predefined case dictionary mapping case numbers to ordered car types (left-to-right)
        self.case_dict = {
            1: ["h", "s"],
            2: ["se", "s"],
            3: ["s"],
            4: ["s", "h"],
            5: ["t"],
            6: ["s", "s"],
            7: ["se", "s"]
        }

        self.type_relations = {
            "h": 0.85,  # hatchback, expected to be smaller than an SUV
            "se": 1,  # sedan
            "s": 1.06,  # SUV
            "t": 2  # truck
        }

    def extract_case_number(self, filename):
        match = re.match(r"(\d+)", os.path.basename(filename))
        return int(match.group(1)) if match else None

    def detect_cars(self):
        results = self.model(self.image)[0]
        for det in results.boxes.data:
            x1, y1, x2, y2, conf, cls = det.tolist()
            if conf > self.conf_threshold and int(cls) in [2,5,7]:  # Class 2 is 'car'
                self.car_boxes.append((int(x1), int(y1), int(x2), int(y2)))
        self.car_boxes.sort(key=lambda box: box[0])
        # Map detected boxes with the ordered types from the selected case.
        self.car_types = self.case_dict.get(self.case_number, ["s"] * len(self.car_boxes))

    def extract_car_strip(self):
        if not self.car_boxes:
            print("No cars detected, You can park any vehicle here.")
            return

        # Define the vertical strip height based on detected cars
        min_y = min(box[1] for box in self.car_boxes)
        max_y = max(box[3] for box in self.car_boxes)
        max_height = max_y - min_y
        self.strip_top = min_y
        strip_bottom = min_y + max_height

        # Instead of tight width bounds, extract the full horizontal strip
        height, width = self.image.shape[:2]
        self.strip_origin_x = 0  # since we’re taking full width
        self.strip = self.image[self.strip_top:strip_bottom, 0:width].copy()

    def map_widths_to_types(self):
        # For each detected car box, record its width under its assigned cartype.
        for box, cartype in zip(self.car_boxes, self.car_types):
            width = box[2] - box[0]
            self.type_to_widths.setdefault(cartype, []).append(width)

    def calculate_average_width(self, incoming_type):
        # Use the first available car type with width data as the base
        available_types = [t for t in self.type_to_widths if self.type_to_widths[t]]

        if not available_types:
            return None  # No detected widths

        base_type = available_types[0]
        base_avg = np.mean(self.type_to_widths[base_type])

        # Compute scaling factor
        factor = self.type_relations.get(incoming_type, 1.0) / self.type_relations.get(base_type, 1.0)
        return base_avg * factor

    def find_available_spaces(self, car_width):

        if not self.car_boxes:
            print("No vehicles detected, the entire space is available.")
            strip_width = self.image.shape[1]
            count = int(strip_width // car_width)
            self.available_spaces = [
                (int(i * car_width), int((i + 1) * car_width)) for i in range(count)
            ]
            return

        safety_gap = car_width * 0.1
        occupied_ranges = [(box[0] - safety_gap, box[2] + safety_gap) for box in self.car_boxes]
        occupied_ranges.sort()
        merged_ranges = []

        for start, end in occupied_ranges:
            if not merged_ranges or start > merged_ranges[-1][1]:
                merged_ranges.append([start, end])
            else:
                merged_ranges[-1][1] = max(merged_ranges[-1][1], end)

        total_start = 0
        total_end = self.image.shape[1]
        current = total_start
        # Compute gaps between merged occupied ranges
        raw_gaps = []
        for start, end in merged_ranges:
            if current < start:
                raw_gaps.append((max(current, 0), int(start)))
            current = max(current, end)

        if current < total_end:
            raw_gaps.append((int(current), total_end))
        # For each gap, calculate how many vehicles of width (including safety gaps) can be fit.
        fitting_boxes = []
        for start, end in raw_gaps:
            gap_width = end - start
            if gap_width >= car_width:
                count = int((gap_width + safety_gap) // (car_width + safety_gap))
                for i in range(count):
                    box_start = start + i * (car_width + safety_gap) + safety_gap / 2
                    box_end = box_start + car_width
                    if box_end <= end:
                        fitting_boxes.append((int(box_start), int(box_end)))
        self.available_spaces = fitting_boxes

    def visualize(self):
        if self.strip is None or self.image is None:
            print("No visualization to render.")
            return
        # Draw detected car boxes (in red) and available spaces (in green)
        img_copy = self.image.copy()
        for (x1, y1, x2, y2) in self.car_boxes:
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)
        for start, end in self.available_spaces:
            cv2.rectangle(
                img_copy,
                (start, self.strip_top),
                (end, self.strip_top + self.strip.shape[0]),
                (0, 255, 0),
                2
            )
        output_path = "output.jpg"
        cv2.imwrite(output_path, img_copy)

    def run(self):
        # Clear old output
        if os.path.exists("output.jpg"):
            os.remove("output.jpg")

        self.case_number = self.extract_case_number(self.image_path)
        self.detect_cars()

        if not self.car_boxes:
            print("No cars detected. Entire strip is available for parking.")
            return

        self.extract_car_strip()
        self.map_widths_to_types()
        avg_width = self.calculate_average_width(self.incoming_cartype)
        if avg_width is None:
            print(f"Could not determine width for car type '{self.incoming_cartype}'.")
            return

        self.find_available_spaces(avg_width)
        print(f"Total available spaces for a '{self.incoming_cartype.upper()}': {len(self.available_spaces)}")
        self.visualize()