import streamlit as st
import os
from smart_parking_system import SmartParkingSystem

# Set up
#st.set_page_config(page_title="Smart Parking System", layout="centered")
st.title("🚘 Smart Parking Management System")
st.write("Select a test case and the incoming vehicle type. The system will show where cars can be parked.")

# Path to your test images
TESTCASE_DIR = "test_cases"
test_files = sorted([f for f in os.listdir(TESTCASE_DIR) if f.endswith(('.jpg', '.png'))])

# Select the test case
case_number = st.selectbox("Select a Test Case", [f"Case - {i+1}" for i in range(len(test_files))])

# Get the image path corresponding to the selected case number
image_filename = test_files[int(case_number.split(' - ')[1])-1]
print(image_filename)
input_image_path = os.path.join(TESTCASE_DIR, image_filename)
print(input_image_path)

# Select incoming car type
car_type = st.selectbox("🚗 Select incoming vehicle type", ["h - Hatchback", "se - Sedan", "s - SUV", "t - Truck"])
car_type_code = car_type.split(" - ")[0]

# Process button
if st.button("🧠 Analyze Parking Area"):
    try:
        # Show original test case image
        st.subheader("📸 Input Image")
        st.image(input_image_path, caption=f"Test Case: {case_number}", use_container_width=True)

        # Run the parking detection logic
        detector = SmartParkingSystem(input_image_path, car_type_code)
        detector.run()

        # Show output if available
        st.subheader("🅿️ Parking Availability")
        if os.path.exists("output.jpg"):
            st.success(f"✅ Estimated available spaces for a '{car_type.upper()}': {len(detector.available_spaces)}")
            st.image("output.jpg", caption="📍 Detected Cars & Available Spaces", use_container_width=True)
        else:
            st.info("No vehicles detected. Entire strip is available for parking.")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
