import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page setup ---
st.set_page_config(
    page_title="Grapevine Photo | Event Sign-Up",
    page_icon="📸",
    layout="centered",
)

# --- Logo and header ---
st.image("https://raw.githubusercontent.com/jscowsert-lang/qr-name-generator/main/Logo-01.jpg", width=300)
st.markdown(
    """
    ## **Event Headshot Sign-Up**
    Please enter your name and email to receive your professional headshot.
    ---
    """
)

CSV_FILE = "signups.csv"

# --- Load existing data ---
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["first_name", "last_name", "email", "timestamp"])

# --- Form ---
with st.form("signup_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    first_name = col1.text_input("First Name", "")
    last_name = col2.text_input("Last Name", "")
    email = st.text_input("Email Address", "")
    submitted = st.form_submit_button("Submit", use_container_width=True)

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
            st.success(f"✅ Thanks, {first_name}! You’ve been added to the sign-up list.")

# --- View / Manage Signups ---
st.markdown("---")
st.subheader("📋 Current Sign-Ups")
st.dataframe(df, use_container_width=True)

# --- Download & Clear buttons ---
col_a, col_b = st.columns(2)

with col_a:
    st.download_button(
        "📥 Download Sign-Ups (CSV)",
        data=df.to_csv(index=False),
        file_name="signups.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_b:
    if st.button("🧹 Clear All Sign-Ups", use_container_width=True):
        df = pd.DataFrame(columns=["first_name", "last_name", "email", "timestamp"])
        df.to_csv(CSV_FILE, index=False)
        st.warning("✅ Sign-up list cleared for a new event.")

