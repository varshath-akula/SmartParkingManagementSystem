import streamlit as st
import os
from smart_parking_system import SmartParkingSystem

# Title and description
st.title("🚘 Smart Parking Management System")
st.write("Upload an image or select a test case and choose the incoming vehicle type. The system will analyze parking availability.")

# Constants
TESTCASE_DIR = "test_cases"
test_files = sorted([f for f in os.listdir(TESTCASE_DIR) if f.endswith(('.jpg', '.png'))])

# Image input mode selection
input_mode = st.radio("Choose image input method:", ["📁 Upload Image", "🧪 Use Test Case"])

# Initialize input image path
input_image_path = None
uploaded_image = None

# Handle user input
if input_mode == "📁 Upload Image":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    if uploaded_image:
        input_image_path = os.path.join("uploaded_image.jpg")
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())

elif input_mode == "🧪 Use Test Case":
    case_number = st.selectbox("Select a Test Case", [f"Case - {i+1}" for i in range(len(test_files))])
    image_filename = test_files[int(case_number.split(' - ')[1]) - 1]
    input_image_path = os.path.join(TESTCASE_DIR, image_filename)

# Select incoming car type
car_type = st.selectbox("🚗 Select incoming vehicle type", ["h - Hatchback", "se - Sedan", "s - SUV", "t - Truck"])
car_type_code = car_type.split(" - ")[0]

# Analyze parking when button is clicked
if st.button("🧠 Analyze Parking Area"):
    if input_image_path is None:
        st.warning("Please upload an image or select a test case.")
    else:
        try:
            st.subheader("📸 Input Image")
            st.image(input_image_path, caption="Selected Input", use_container_width=True)

            detector = SmartParkingSystem(input_image_path, car_type_code)
            detector.run()

            st.subheader("🅿️ Parking Availability")
            if os.path.exists("output.jpg"):
                st.success(f"✅ Estimated available spaces for a '{car_type.upper()}': {len(detector.available_spaces)}")
                st.image("output.jpg", caption="📍 Detected Cars & Available Spaces", use_container_width=True)
            else:
                st.info("No vehicles detected. Entire strip is available for parking.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
