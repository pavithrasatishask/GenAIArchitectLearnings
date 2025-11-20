import streamlit as st
import requests

st.set_page_config(page_title="Unit Converter", page_icon="🔄", layout="centered")

# ---- Session State History ----
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🔄 Unit Converter")
st.write("Convert currency, temperature, length, and weight with real-time results!")

# ---- Currency Conversion function (Live API) ----
def get_usd_inr_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url).json()
        return response["rates"]["INR"]   # 1 USD = ? INR
    except:
        return None

# ---- Converter Functions ----
def convert_temperature(value, direction):
    if direction == "C → F":
        return (value * 9/5) + 32
    elif direction == "F → C":
        return (value - 32) * 5/9

def convert_length(value, direction):
    if direction == "cm → inch":
        return value / 2.54
    elif direction == "inch → cm":
        return value * 2.54

def convert_weight(value, direction):
    if direction == "kg → lb":
        return value * 2.20462
    elif direction == "lb → kg":
        return value / 2.20462

def convert_currency(value, direction):
    rate = get_usd_inr_rate()
    if rate is None:
        st.error("Unable to fetch live currency rate.")
        return None
    
    if direction == "INR → USD":
        return value / rate
    elif direction == "USD → INR":
        return value * rate


# ---- User Interface ----
conversion_type = st.selectbox(
    "Select conversion type",
    ["Currency (INR ↔ USD)", "Temperature (°C ↔ °F)", "Length (cm ↔ inch)", "Weight (kg ↔ lb)"]
)

# ---- Direction Options ----
options_map = {
    "Currency (INR ↔ USD)": ["INR → USD", "USD → INR"],
    "Temperature (°C ↔ °F)": ["C → F", "F → C"],
    "Length (cm ↔ inch)": ["cm → inch", "inch → cm"],
    "Weight (kg ↔ lb)": ["kg → lb", "lb → kg"]
}

direction = st.radio("Direction", options_map[conversion_type], horizontal=True)

value = st.number_input("Enter value:", min_value=0.0, format="%.4f")

if st.button("Convert"):
    result = None

    if conversion_type.startswith("Currency"):
        result = convert_currency(value, direction)
    elif conversion_type.startswith("Temperature"):
        result = convert_temperature(value, direction)
    elif conversion_type.startswith("Length"):
        result = convert_length(value, direction)
    elif conversion_type.startswith("Weight"):
        result = convert_weight(value, direction)

    if result is not None:
        st.success(f"Converted Value: **{result:.4f}**")

        # Add to History
        st.session_state.history.append({
            "Type": conversion_type,
            "Direction": direction,
            "Input": value,
            "Output": round(result, 4)
        })

# ---- History Table ----
st.subheader("📜 Conversion History")
if len(st.session_state.history) == 0:
    st.info("No conversions yet.")
else:
    st.table(st.session_state.history)
