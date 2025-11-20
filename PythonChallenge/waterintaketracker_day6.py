import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Water Intake Tracker 💧", layout="centered")

# ---- Initialize Session State ----
if "water_log" not in st.session_state:
    st.session_state.water_log = {}  # date -> total ml

GOAL = 3000  # 3 liters


# ---- Title ----
st.title("💧 Water Intake Tracker")
st.write("Log your water intake and track your progress toward 3 liters per day.")


# ---- Log Water Intake ----
st.subheader("➕ Log Intake")

selected_date = st.date_input(
    "Select Date",
    value=datetime.date.today(),
    max_value=datetime.date.today()
)

amount = st.number_input("Enter amount (ml):", min_value=0, step=50)

if st.button("Add Entry"):
    date_key = selected_date.isoformat()

    # Update log for this date
    st.session_state.water_log[date_key] = st.session_state.water_log.get(date_key, 0) + amount
    st.success(f"Added {amount} ml for {date_key}!")


# ---- Today's Progress ----
today = datetime.date.today().isoformat()
today_total = st.session_state.water_log.get(today, 0)

st.subheader("📅 Today's Progress")
progress = min(today_total / GOAL, 1.0)
st.progress(progress)
st.write(f"**{today_total} ml / {GOAL} ml**")

if today_total >= GOAL:
    st.success("🎉 Goal Achieved! Great job staying hydrated!")
else:
    st.info(f"You need **{GOAL - today_total} ml** more to reach today's goal.")


# ---- Weekly Chart ----
st.subheader("📊 Weekly Hydration Chart (Last 7 Days)")

# Prepare 7-day window (today → past 6 days)
dates = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
values = [st.session_state.water_log.get(d, 0) for d in dates]

df_chart = pd.DataFrame({
    "Date": dates,
    "Water Intake (ml)": values
}).set_index("Date")

st.bar_chart(df_chart)


# ---- History Table ----
st.subheader("📜 Intake History")

if st.session_state.water_log:
    df = pd.DataFrame([
        {"Date": d, "Total (ml)": ml}
        for d, ml in sorted(st.session_state.water_log.items())
    ])
    st.table(df)
else:
    st.info("No water intake logged yet.")
