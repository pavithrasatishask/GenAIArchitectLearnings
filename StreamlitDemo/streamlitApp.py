import streamlit as st
import pandas as pd
import requests
from datetime import date
import matplotlib.pyplot as plt

API_BASE = "http://localhost:5000"

def get_categories(trans_type):
    url = f"{API_BASE}/categories/{'expense' if trans_type == 'Expense' else 'income'}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def add_transaction_api(tx):
    url = f"{API_BASE}/transaction"
    response = requests.post(url, json=tx)
    return response.status_code == 200

def fetch_transactions_api():
    url = f"{API_BASE}/transaction"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def update_transaction_api(tx_id, tx):
    url = f"{API_BASE}/transaction/{tx_id}"
    response = requests.put(url, json=tx)
    return response.status_code == 200

def delete_transaction_api(tx_id):
    url = f"{API_BASE}/transaction/{tx_id}"
    response = requests.delete(url)
    return response.status_code == 200

st.title("Cash Wallet - Transactions")

# Add transaction form (outside table as before)
if 'trans_type' not in st.session_state:
    st.session_state['trans_type'] = "Expense"
if 'category' not in st.session_state:
    st.session_state['category'] = None
if 'edit_row' not in st.session_state:
    st.session_state['edit_row'] = None  # ID of row currently being edited

st.session_state['trans_type'] = st.radio("Type", ["Expense", "Income"], index=0)
category_options = get_categories(st.session_state['trans_type'])
if st.session_state['category'] not in category_options:
    st.session_state['category'] = category_options[0] if category_options else None
st.session_state['category'] = st.selectbox(
    "Category", category_options,
    index=category_options.index(st.session_state['category']) if st.session_state['category'] in category_options else 0
)

with st.form("Add Transaction", clear_on_submit=True):
    date_ = st.date_input("Date", value=date.today())
    note = st.text_input("Note (optional)")
    amount = st.number_input("Amount", value=0.0, step=0.01, format="%.2f")
    submitted = st.form_submit_button("Add transaction")
    if submitted and amount != 0:
        tx_amount = -abs(amount) if st.session_state['trans_type'] == "Expense" else abs(amount)
        tx = {
            'date': str(date_),
            'type': st.session_state['trans_type'],
            'category': st.session_state['category'],
            'note': note,
            'amount': tx_amount
        }
        success = add_transaction_api(tx)
        if success:
            st.success("Transaction added!")
        else:
            st.error("Failed to add transaction!")

# Table with inline edit/delete
st.subheader("Transaction List")
transactions = fetch_transactions_api()
if transactions:
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date', ascending=False)

    for i, tx in df.iterrows():
        # Determine if the current row is "in edit mode"
        editing = st.session_state['edit_row'] == int(tx['id'])
        cols = st.columns([1,2,2,2,3,2,2,2])
        cols[0].write(int(tx['id']))  # ID
        if not editing:
            cols[1].write(tx['date'].date())
            cols[2].write(tx['type'])
            cols[3].write(tx['category'])
            cols[4].write(tx['note'])
            cols[5].write(f"{tx['amount']:.2f}")
            if cols[6].button("✏️", key=f"edit_{tx['id']}"):
                st.session_state['edit_row'] = int(tx['id'])
            if cols[7].button("🗑️", key=f"del_{tx['id']}"):
                deleted = delete_transaction_api(tx['id'])
                if deleted:
                    st.success(f"Entry {tx['id']} deleted! Please refresh to see changes.")
                else:
                    st.error("Delete failed!")
        else:
            # Editing fields, except category/type (category is shown, not editable)
            edit_date = cols[1].date_input("Date", value=tx['date'].date(), key=f"date_{tx['id']}")
            cols[2].write(tx['type'])
            cols[3].write(tx['category'])
            edit_note = cols[4].text_input("Note", value=tx['note'], key=f"note_{tx['id']}")
            edit_amount = cols[5].number_input("Amount", value=float(tx['amount']), step=0.01, format="%.2f", key=f"amt_{tx['id']}")

            # Two action buttons: Save/Cancel
            if cols[6].button("💾", key=f"save_{tx['id']}"):
                edit_amount_final = -abs(edit_amount) if tx['type'] == "Expense" else abs(edit_amount)
                success = update_transaction_api(tx['id'], {
                    "date": str(edit_date),
                    "type": tx['type'],
                    "category": tx['category'],
                    "note": edit_note,
                    "amount": edit_amount_final
                })
                if success:
                    st.success(f"Entry {tx['id']} updated! Please refresh to see changes.")
                    st.session_state['edit_row'] = None
                else:
                    st.error("Update failed!")
            if cols[7].button("❌", key=f"cancel_{tx['id']}"):
                st.session_state['edit_row'] = None

else:
    st.info("No transactions yet.")

# Wallet summary
if transactions:
    df = pd.DataFrame(transactions)
    wallet_balance = df['amount'].sum()
    total_expense = df[df['amount'] < 0]['amount'].sum()
    total_income = df[df['amount'] > 0]['amount'].sum()
    st.metric("Current Wallet Balance", f"{wallet_balance:,.2f} USD")
    st.metric("Total Period Expenses", f"{total_expense:,.2f} USD")
    st.metric("Total Period Income", f"{total_income:,.2f} USD")

import matplotlib.pyplot as plt

if transactions:
    df = pd.DataFrame(transactions)
    spent = abs(df[df['amount'] < 0]['amount'].sum())      # Total expenses (absolute value)
    available = df['amount'].sum()                         # Wallet balance (can be negative)
    total_income = df[df['amount'] > 0]['amount'].sum()
    available_balance = total_income - spent

    pie_labels = ['Spent', 'Available Balance']
    pie_values = [spent, available_balance if available_balance >= 0 else 0]

    fig, ax = plt.subplots()
    ax.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', startangle=90, colors=['#ff6666','#66b3ff'])
    ax.axis('equal')
    st.subheader("Spent vs Available Balance")
    st.pyplot(fig)
