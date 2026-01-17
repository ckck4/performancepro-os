# app/pages/5_eval_and_account_entry.py
import sys
import os

# Add project root (two levels up) to Python import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from datetime import date
from db.database import SessionLocal
from db.models import EvaluationProgram, Evaluation, FundedAccount

st.set_page_config(page_title="Evaluations & Funded Accounts", layout="wide")
st.title("Add Evaluations and Funded Accounts")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Evaluation form ---
with st.form("evaluation_form"):
    st.subheader("New Evaluation Purchase")
    program_firm = st.text_input("Prop firm")
    program_model = st.text_input("Program model (e.g. two‑phase, one‑phase)")
    program_rules = st.text_area("Rules", value="")
    program_price = st.number_input("Program price", min_value=0.0, value=0.0)
    eval_purchase_date = st.date_input("Purchase date", value=date.today())
    eval_status = st.selectbox(
        "Status", ["bought", "active", "passed", "failed", "expired"]
    )
    attempts_count = st.number_input("Attempts count", min_value=0, value=0, step=1)
    resets_count = st.number_input("Resets count", min_value=0, value=0, step=1)
    cost_total = st.number_input(
        "Total cost (0 uses program price)", min_value=0.0, value=0.0
    )
    submit_eval = st.form_submit_button("Save Evaluation")

if submit_eval:
    if not program_firm or not program_model:
        st.error("Both firm and program model are required.")
    else:
        with SessionLocal() as db:
            # Find or create the evaluation program
            program = (
                db.query(EvaluationProgram)
                .filter_by(firm=program_firm, model=program_model)
                .first()
            )
            if not program:
                program = EvaluationProgram(
                    firm=program_firm,
                    model=program_model,
                    rules=program_rules,
                    price=program_price,
                )
                db.add(program)
                db.commit()
                db.refresh(program)
            # Use program price if cost_total is zero
            if cost_total == 0.0:
                cost_total = program.price or 0.0
            evaluation = Evaluation(
                program_id=program.id,
                purchase_date=eval_purchase_date,
                status=eval_status,
                attempts_count=attempts_count,
                resets_count=resets_count,
                cost_total=cost_total,
            )
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)
        st.success(f"Evaluation saved with ID {evaluation.id}.")

# --- Funded account form ---
with st.form("funded_account_form"):
    st.subheader("New Funded Account")
    account_firm = st.text_input("Firm", key="fa_firm")
    start_date = st.date_input("Start date", value=date.today(), key="fa_start_date")
    account_status = st.selectbox(
        "Status", ["active", "closed"], key="fa_status"
    )
    account_size = st.number_input(
        "Account size", min_value=0.0, step=1000.0, key="fa_size"
    )
    drawdown_buffer = st.number_input(
        "Current drawdown buffer", min_value=0.0, key="fa_buffer"
    )
    # Fetch existing evaluations (for optional linking)
    with next(get_db()) as db:
        evals = db.query(Evaluation).all()
    eval_options = ["None"] + [str(e.id) for e in evals]
    selected_eval = st.selectbox(
        "Linked Evaluation (optional)", eval_options, key="fa_eval"
    )
    submit_account = st.form_submit_button("Save Funded Account")

if submit_account:
    if not account_firm:
        st.error("Firm is required.")
    else:
        with SessionLocal() as db:
            eval_id = None
            if selected_eval != "None":
                eval_id = int(selected_eval)
            funded_account = FundedAccount(
                firm=account_firm,
                start_date=start_date,
                status=account_status,
                account_size=account_size,
                current_drawdown_buffer=drawdown_buffer,
                evaluation_id=eval_id,
            )
            db.add(funded_account)
            db.commit()
            db.refresh(funded_account)
        st.success(f"Funded account saved with ID {funded_account.id}.")
