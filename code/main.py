import streamlit as st
import pandas as pd

st.title("Birth Chart Generator")

with st.form("birth_chart_form"):
    st.header("Enter your birth details")
    name = st.text_input("Your Name:")
    date = st.date_input("Date of birth:", 
                        min_value=pd.to_datetime("1900-01-01").date(),
                        max_value=pd.to_datetime("today").date())
    time = st.time_input("Time of birth:", value=pd.to_datetime("00:00").time())
    location = st.text_input("Place of birth:")

    submitted = st.form_submit_button("Calculate Birth Chart...")

if submitted:
    st.success("Form submitted successfully!")
