# app/pages/2_session_entry.py
import sys
import os

# Add project root (two levels up) to Python import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from datetime import datetime
from db.database import SessionLocal
from db.models import Session, Tag

st.set_page_config(page_title="Session Entry", layout="wide")
st.title("Enter a New Session")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fetch existing tags
with next(get_db()) as db:
    tags = db.query(Tag).all()
tag_names = [t.name for t in tags]

with st.form("session_form"):
    date = st.date_input("Session date", value=datetime.now().date())
    start_time = st.time_input("Start time", value=datetime.now().time())
    end_time = st.time_input("End time", value=datetime.now().time())
    market = st.text_input("Market (e.g. CME Globex)")
    notes = st.text_area("Notes")
    selected_tags = st.multiselect("Tags", tag_names)
    submit = st.form_submit_button("Save Session")

if submit:
    if end_time < start_time:
        st.error("End time cannot be earlier than start time.")
    else:
        with next(get_db()) as db:
            sess = Session(
                date=date,
                start_time=datetime.combine(date, start_time),
                end_time=datetime.combine(date, end_time),
                market=market,
                notes=notes,
            )
            tag_objs = [t for t in tags if t.name in selected_tags]
            sess.tags = tag_objs
            db.add(sess)
            db.commit()
            st.success(f"Session {sess.id} saved successfully!")
