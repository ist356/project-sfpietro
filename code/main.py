import requests
import time
import pytz
from datetime import datetime as dt
import pandas as pd
import streamlit as st
from functions import *

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

def submit_form():
    st.session_state.form_submitted = True

with st.form("birth_chart_form"):
    st.title("Birth Chart Generator")
    st.header("Enter your birth details")
    name = st.text_input("Your Name:")
    birth_date = st.date_input("Date of birth:", 
                        min_value=pd.to_datetime("1900-01-01").date(),
                        max_value=pd.to_datetime("today").date())
    birth_time = st.time_input("Time of birth:", value=pd.to_datetime("00:00").time())
    birth_place = st.text_input("Place of birth:")

    submitted = st.form_submit_button("Calculate Birth Chart...", on_click=submit_form)

if st.session_state.form_submitted:
    #st.success("Form submitted successfully!")
    st.header(f"{name}'s Birth Chart:")
    lat, lon = get_lat_lon(birth_place)
    if lat and lon:
        city, nation = reverse_geocode(lat,lon)
        timezone = get_timezone(lat,lon)
        raw = get_birth_chart_data(name, birth_date, birth_time, lat, lon, city, nation, timezone)
        planets_df = process_birth_chart(raw)
        big_three = get_big_three(raw, planets_df)
        st.caption("Big Three:")
        for key, value in big_three.items():
            st.text(f"Your {key} sign is {value}")
        st.dataframe(planets_df)

    if st.button("Get Daily Horoscope"):
        main_sign = big_three['sun']
        horoscope = get_horoscope_data(main_sign)
        st.write(f'"{horoscope}"')


'''
Whats left to do:
- hover feature of details
- google api to complete search for birth_place
- make it look pretty

- create test code

'''
