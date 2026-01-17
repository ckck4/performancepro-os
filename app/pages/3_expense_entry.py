# app/pages/3_expense_entry.py
import sys
import os

# Add project root (two levels up) to Python import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from datetime import date
from db.database import SessionLocal
from db.models import Vendor, Expense, Evaluation, FundedAccount

st.set_page_config(page_title="Expense Entry", layout="wide")
st.title("Enter a New Expense")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

with st.form("expense_form"):
    exp_date = st.date_input("Expense date", value=date.today())
    vendor_name = st.text_input("Vendor name")
    category = st.text_input("Category (e.g. eval, reset, subscription, data, misc)")
    amount = st.number_input("Amount", min_value=0.0)
    currency = st.text_input("Currency (e.g. USD, EUR)", value="USD")
    notes = st.text_area("Notes", value="")
    evaluation_id = st.number_input("Evaluation ID (optional, 0 = none)", min_value=0, step=1, value=0)
    account_id = st.number_input("Funded Account ID (optional, 0 = none)", min_value=0, step=1, value=0)
    submit = st.form_submit_button("Save Expense")

if submit:
    if not vendor_name:
        st.error("Vendor name is required.")
    else:
        with SessionLocal() as db:
            # Find or create the vendor
            vendor = db.query(Vendor).filter_by(name=vendor_name).first()
            if not vendor:
                vendor = Vendor(name=vendor_name, category=category)
                db.add(vendor)
                db.commit()
                db.refresh(vendor)
            # Look up optional links
            evaluation = db.query(Evaluation).get(int(evaluation_id)) if evaluation_id else None
            account = db.query(FundedAccount).get(int(account_id)) if account_id else None
            # Create and save the expense
            expense = Expense(
                date=exp_date,
                vendor_id=vendor.id,
                category=category,
                amount=amount,
                currency=currency,
                notes=notes,
                evaluation_id=evaluation.id if evaluation else None,
                account_id=account.id if account else None,
            )
            db.add(expense)
            db.commit()
        st.success("Expense saved successfully!")
