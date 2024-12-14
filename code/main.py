import requests
import time
import pytz
from datetime import datetime as dt
import pandas as pd
import streamlit as st
from functions import *

st.title("Birth Chart Generator")

with st.form("birth_chart_form"):
    st.header("Enter your birth details")
    name = st.text_input("Your Name:")
    birth_date = st.date_input("Date of birth:", 
                        min_value=pd.to_datetime("1900-01-01").date(),
                        max_value=pd.to_datetime("today").date())
    birth_time = st.time_input("Time of birth:", value=pd.to_datetime("00:00").time())
    birth_place = st.text_input("Place of birth:")

    submitted = st.form_submit_button("Calculate Birth Chart...")

if submitted:
    #st.success("Form submitted successfully!")

    lat, lon = get_lat_lon(birth_place)
    if lat and lon:
        city, nation = reverse_geocode(lat,lon)
        timezone = get_timezone(lat,lon)
        raw = get_birth_chart_data(name, birth_date, birth_time, lat, lon, city, nation, timezone)
        planets_df = process_birth_chart(raw)
        big_three = get_big_three(raw, planets_df)
        st.header("Big Three:")
        for key, value in big_three.items():
            st.text(f"Your {key} sign is {sign}")
        st.dataframe(planets_df)


'''
Whats left to do:
- get more requests for this api!!!
- daily horoscope
- hover feature of details
- google api to complete search for birth_place
- make it look pretty

- create test code

'''
