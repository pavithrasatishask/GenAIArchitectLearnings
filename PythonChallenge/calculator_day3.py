import streamlit as st

# Set up page
st.set_page_config(page_title="Smart Calculator", layout="centered")

# Custom CSS styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #FF512F, #F09819, #FFD200);
    }
    .main {
        background-color: transparent;
    }
    div[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #FF512F, #F09819, #FFD200);
    }
    
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        height: 45px;
    }
    .result-box {
        background-color: #d4edda;
        color: #155724;
        border-radius: 10px;
        padding: 15px;
        font-size: 20px;
        margin-top: 20px;
        text-align: center;
        font-weight: 600;
    }
    .title-box {
        background-color: #2c3e50;
        color: white;
        border-radius: 10px 10px 0 0;
        padding: 15px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown("""
<div class="title-box">
    <h2>🧮 Smart Calculator</h2>
</div>
""", unsafe_allow_html=True)

# Content box
with st.container():
    st.markdown('<div class="calc-box">', unsafe_allow_html=True)

    # Inputs
    num1 = st.number_input("🔢 First Number:", step=1.0)
    num2 = st.number_input("🔢 Second Number:", step=1.0)
    operation = st.selectbox("⚙️ Operation:", 
        ("Addition (+)", "Subtraction (−)", "Multiplication (×)", "Division (÷)"))
    

    # Buttons
    col1, col2 = st.columns(2)
    calc = col1.button("🚀 Calculate")
    clear = col2.button("🧹 Clear All")

    # Session state for result and history
    if "result" not in st.session_state:
        st.session_state.result = None
    if "history" not in st.session_state:
        st.session_state.history = []

    # Logic
    if calc:
        try:
            if operation == "Addition (+)":
                res = num1 + num2
                symbol = "+"
            elif operation == "Subtraction (−)":
                res = num1 - num2
                symbol = "-"
            elif operation == "Multiplication (×)":
                res = num1 * num2
                symbol = "×"
            elif operation == "Division (÷)":
                if num2 == 0:
                    st.error("Division by zero is not allowed!")
                    res = None
                else:
                    res = num1 / num2
                    symbol = "÷"

            if res is not None:
                st.session_state.result = res
                st.session_state.history.append(f"{num1} {symbol} {num2} = {res}")
        except Exception as e:
            st.error(f"Error: {e}")

    if clear:
        st.session_state.result = None
        st.session_state.history.clear()

    # Show result
    if st.session_state.result is not None:
        st.markdown(f"<div class='result-box'>✅ Result: {st.session_state.result}</div>", unsafe_allow_html=True)
        #st.markdown(f"🧩 **Calculation:** {num1} {symbol} {num2} = {st.session_state.result}")

    # Show history
    if st.session_state.history:
        st.markdown("### 🕒 Calculation History")
        for entry in reversed(st.session_state.history):
            st.markdown(f"- {entry}")

    st.markdown('</div>', unsafe_allow_html=True)
