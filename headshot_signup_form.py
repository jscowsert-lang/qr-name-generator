import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page setup ---
st.set_page_config(
    page_title="DFW Headshot Professionals | Event Sign-Up",
    page_icon="📝",
    layout="centered",
)

# --- Branding header ---
st.image("https://raw.githubusercontent.com/jscowsert-lang/qr-name-generator/main/Logo-01.jpg", width=300)
st.markdown(
    """
    ### **DFW Headshot Professionals — Event Sign-Up**
    Please enter your name and email to receive your professional headshot.
    ---
    """
)

# --- File path for storing sign-ups ---
CSV_FILE = "signups.csv"

# --- Load existing data if any ---
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["first_name", "last_name", "email", "timestamp"])

# --- Sign-Up Form ---
with st.form("signup_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    first_name = col1.text_input("First Name")
    last_name = col2.text_input("Last Name")
    email = st.text_input("Email Address")

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not first_name or not last_name or not email:
            st.error("⚠️ Please fill out all fields before submitting.")
        else:
            new_row = {
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "email": email.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Thank you, {first_name}! You’ve been added to the sign-up list.")

# --- View / Download Data ---
st.markdown("---")
st.subheader("📋 Current Sign-Ups")
st.dataframe(df)

st.download_button(
    label="📥 Download Sign-Ups as CSV",
    data=df.to_csv(index=False),
    file_name="signups.csv",
    mime="text/csv",
)

