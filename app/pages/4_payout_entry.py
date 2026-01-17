# app/pages/4_payout_entry.py
import sys
import os

# Add project root (two levels up) to Python import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from datetime import date
from db.database import SessionLocal
from db.models import FundedAccount, Payout

st.set_page_config(page_title="Payout Entry", layout="wide")
st.title("Enter a New Payout")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Retrieve funded accounts to populate the dropdown
with next(get_db()) as db:
    accounts = db.query(FundedAccount).all()
account_options = [
    f"{acc.id} – {acc.firm} (start {acc.start_date})" for acc in accounts
]

with st.form("payout_form"):
    payout_date = st.date_input("Payout date", value=date.today())
    firm = st.text_input("Prop firm")
    selected_account = st.selectbox("Funded account", account_options)
    amount_gross = st.number_input("Gross amount", min_value=0.0)
    fees_withheld = st.number_input("Fees withheld", min_value=0.0)
    amount_net = st.number_input(
        "Net amount (leave 0 to auto‑compute)", min_value=0.0, value=0.0
    )
    submit = st.form_submit_button("Save Payout")

if submit:
    if not firm:
        st.error("Prop firm is required.")
    else:
        with SessionLocal() as db:
            # Parse the selected account ID from the dropdown
            account_id = int(selected_account.split("–")[0].strip())
            if amount_net == 0.0:
                amount_net = amount_gross - fees_withheld
            payout = Payout(
                date=payout_date,
                firm=firm,
                account_id=account_id,
                amount_gross=amount_gross,
                fees_withheld=fees_withheld,
                amount_net=amount_net,
            )
            db.add(payout)
            db.commit()
        st.success("Payout saved successfully!")
