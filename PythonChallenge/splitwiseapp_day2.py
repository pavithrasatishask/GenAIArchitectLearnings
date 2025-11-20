import streamlit as st
import pandas as pd
import altair as alt
from io import StringIO

# Page configuration
st.set_page_config(page_title="Expense Splitter", page_icon="💸", layout="wide")

# Enhanced styling
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-top: 0;
        }
        .section-box {
            background-color: #ffffffcc;
            backdrop-filter: blur(6px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        .result-box {
            background-color: #ffffffee;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .footer-note {
            text-align: center;
            color: #444;
            margin-top: 20px;
            font-size: 0.95rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>💸 Friends Expense Splitter</h1>", unsafe_allow_html=True)

# Input sections side by side
left_input, right_input = st.columns(2)

with left_input:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("Enter Expense Details")
    total_amount = st.number_input("Total Amount (₹)", min_value=0.0, step=100.0)
    num_people = st.number_input("Number of People", min_value=1, step=1)
    st.markdown("</div>", unsafe_allow_html=True)

with right_input:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("Enter Names and Contributions")
    names, contributions = [], []
    if num_people:
        for i in range(int(num_people)):
            c1, c2 = st.columns([1, 1])
            with c1:
                name = st.text_input(f"Name {i+1}", key=f"name_{i}")
            with c2:
                contributed = st.number_input(
                    f"Contributed by {name or 'Person ' + str(i+1)} (₹)",
                    min_value=0.0,
                    step=50.0,
                    key=f"contribution_{i}"
                )
            names.append(name or f"Person {i+1}")
            contributions.append(contributed)
    st.markdown("</div>", unsafe_allow_html=True)

# Action button
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
calculate_clicked = st.button("🔹 Calculate Split 🔹")
st.markdown("</div>", unsafe_allow_html=True)

# Results section
if calculate_clicked:
    if total_amount == 0:
        st.warning("Please enter a total amount greater than 0.")
    else:
        equal_share = total_amount / num_people
        results = []
        for i in range(int(num_people)):
            balance = round(contributions[i] - equal_share, 2)
            status = "Gets Back" if balance > 0 else "Owes"
            results.append({
                "Name": names[i],
                "Contribution": contributions[i],
                "Balance": abs(balance),
                "Status": status
            })
        df = pd.DataFrame(results)

        left_display, right_display = st.columns(2)
        with left_display:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("💰 Split Summary Table")
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.info(f"Each person should ideally pay ₹{equal_share:.2f}")
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                "📄 Download CSV",
                csv_buffer.getvalue(),
                "expense_split_results.csv",
                "text/csv"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with right_display:
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("📊 Balance Overview Chart")
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('Name:N', sort=None),
                y='Balance:Q',
                color='Status:N',
                tooltip=['Name', 'Status', 'Balance']
            ).properties(width='container', height=400)
            st.altair_chart(chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer-note'>Design © 2025 | Expense Splitter for Friends</div>", unsafe_allow_html=True)
