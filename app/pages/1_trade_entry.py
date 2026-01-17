# app/pages/1_trade_entry.py
import sys
import os

# Add project root (two levels up) to Python import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from datetime import datetime
from db.database import SessionLocal
from db.models import Instrument, Strategy, Tag, Trade, Session as TradeSession

st.set_page_config(page_title="Trade Entry", layout="wide")
st.title("Enter a New Trade")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fetch choices from the DB
with next(get_db()) as db:
    instruments = db.query(Instrument).all()
    strategies = db.query(Strategy).all()
    tags = db.query(Tag).all()
    sessions = db.query(TradeSession).order_by(TradeSession.date.desc()).all()

instrument_names = [f"{inst.symbol} ({inst.name or ''})" for inst in instruments]
strategy_names = [s.name for s in strategies]
tag_names = [t.name for t in tags]
session_options = [
    f"{s.id} – {s.date} {s.start_time or ''}-{s.end_time or ''}" for s in sessions
]

with st.form("trade_form"):
    selected_session = st.selectbox("Session", session_options if session_options else ["No sessions yet"], index=0)
    selected_instrument = st.selectbox("Instrument", instrument_names)
    qty = st.number_input("Quantity (# contracts)", min_value=1, step=1)
    direction = st.selectbox("Direction", ["LONG", "SHORT"])
    entry_price = st.number_input("Entry price", min_value=0.0, format="%.4f")
    exit_price = st.number_input("Exit price", min_value=0.0, format="%.4f")
    entry_time = st.time_input("Entry time", value=datetime.now().time())
    exit_time = st.time_input("Exit time", value=datetime.now().time())
    fees = st.number_input("Fees & commissions", min_value=0.0, format="%.2f")
    selected_strategy = st.selectbox("Strategy", strategy_names)
    selected_tags = st.multiselect("Tags", tag_names)
    submit = st.form_submit_button("Save Trade")

if submit:
    # Create and commit the Trade
    with next(get_db()) as db:
        # Map names back to objects/ids
        inst_obj = next((i for i in instruments if f"{i.symbol} ({i.name or ''})" == selected_instrument), None)
        strat_obj = next((s for s in strategies if s.name == selected_strategy), None)
        tag_objs = [t for t in tags if t.name in selected_tags]
        sess_obj = None
        if sessions:
            # Extract the session ID from the display string
            sess_id = int(selected_session.split("–")[0].strip())
            sess_obj = db.query(TradeSession).get(sess_id)

        if inst_obj is None or strat_obj is None or sess_obj is None:
            st.error("Please make sure the session, instrument and strategy exist.")
        else:
            trade = Trade(
                session_id=sess_obj.id,
                instrument_id=inst_obj.id,
                strategy_id=strat_obj.id,
                quantity=qty,
                direction=direction,
                entry_price=entry_price,
                exit_price=exit_price,
                entry_time=datetime.combine(sess_obj.date, entry_time),
                exit_time=datetime.combine(sess_obj.date, exit_time),
                fees_commissions=fees,
            )
            # Attach tags
            trade.tags = tag_objs
            db.add(trade)
            db.commit()
            st.success("Trade saved successfully!")
