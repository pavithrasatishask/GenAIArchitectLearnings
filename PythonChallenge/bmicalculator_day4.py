import streamlit as st

st.set_page_config(page_title="Fun BMI Calculator", page_icon="🤸‍♂️")

st.title("Let's Have Fun with Your BMI! 🎉")

# Height input
height_unit = st.selectbox("Select your height unit:", ["Meters", "Centimeters", "Feet"])
height = st.number_input(f"Enter your height in {height_unit}:", min_value=0.1, format="%.2f")

# Weight input
weight_unit = st.selectbox("Select your weight unit:", ["Kilograms", "Pounds"])
weight = st.number_input(f"Enter your weight in {weight_unit}:", min_value=0.1, format="%.2f")

def convert_to_meters(height, unit):
    if unit == "Centimeters":
        return height / 100
    if unit == "Feet":
        return height * 0.3048
    return height

def convert_to_kg(weight, unit):
    if unit == "Pounds":
        return weight * 0.453592
    return weight

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "Remember, your worth isn't defined by a number. Keep shining! 🌟"
    elif 18.5 <= bmi < 25:
        return "Normal weight", "Awesome! Keep celebrating your healthy self! 🎈"
    elif 25 <= bmi < 30:
        return "Overweight", "You're doing great—healthy bodies come in all shapes! 💪"
    else:
        return "Obese", "Every step you take toward health is a victory. Keep going! 💖"

if st.button("Calculate BMI"):
    height_m = convert_to_meters(height, height_unit)
    weight_kg = convert_to_kg(weight, weight_unit)
    bmi = weight_kg / (height_m ** 2)
    category, message = bmi_category(bmi)
    st.success(f"Your BMI is: {bmi:.2f} ({category})")
    st.info(message)
