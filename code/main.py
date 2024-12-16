import requests
import time
import pytz
from datetime import datetime as dt
import pandas as pd
import streamlit as st
from functions import *
import plotly.express as px

st.set_page_config(
    page_title="Birth Chart & Horoscope🌌",
    page_icon="✨",
    layout="wide"
)

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

def submit_form():
    st.session_state.form_submitted = True

image_path = "code/images/banner.jpg"
st.image(image_path, use_container_width=True)

with st.form("birth_chart_form"):
    t1, t2, t3 = st.columns([1,2,1])
    with t2:
        st.title("Birth Chart Generator✨")
        st.header("Enter your birth details")
    form_col1, form_col2 = st.columns(2)
    with form_col1:
        name = st.text_input("Your Name:")
        birth_place = st.text_input("Place of birth: (city, state)")
    with form_col2:
        birth_date = st.date_input("Date of birth:", min_value=pd.to_datetime("1900-01-01").date(),max_value=pd.to_datetime("today").date())
        birth_time = st.time_input("Time of birth: (military)", value=pd.to_datetime("00:00").time())

    submitted = st.form_submit_button("Calculate Birth Chart...", on_click=submit_form)

if st.session_state.form_submitted:
    if not name or not birth_place:
        st.warning("⚠️Please fill in all feilds⚠️")
    else:
        #st.success("Form submitted successfully!")
        lat, lon = get_lat_lon(birth_place)
        if lat and lon:
                city, nation = reverse_geocode(lat,lon)
                timezone = get_timezone(lat,lon)
                raw = get_birth_chart_data(name, birth_date, birth_time, lat, lon, city, nation, timezone)
                planets_df = process_birth_chart(raw)
                big_three = get_big_three(raw, planets_df)
                c1, c2,= st.columns(2)
                with c1:
                    st.header(f"{name}'s Birth Chart🌌")
                    st.caption("Big Three:")
                    for key, value in big_three.items():
                        st.text(f"Your {key} sign is {value}")
                    columns = ['emoji','sign','element','position','house']
                with c2:
                    view = planets_df[columns]
                    st.dataframe(view, use_container_width=True)

                st.header("Birth Chart Visualization")
                col1, col2 = st.columns(2)
                df = planets_df
                with col1:
                    st.caption("Planets in Zodiac Signs")
                    scatter = plot_scatter(planets_df)
                    scatter.update_layout(showlegend=False)
                    st.plotly_chart(scatter)
                with col2:
                    st.caption("Distribution in Zodiac Signs")
                    pie_chart = plot_pie_chart(planets_df)
                    st.plotly_chart(pie_chart)


                second_col1, second_col2 = st.columns(2)
                df = planets_df
                with second_col1:
                    if st.button("Get Daily Horoscope"):
                        main_sign = df.loc[df['name'] == 'Sun', 'sign'].values[0]
                        horoscope = get_horoscope_data(main_sign)
                        if horoscope:
                            st.caption(f'"*{horoscope}*"')
                        else:
                            st.caption(("Could not read horoscope at this time. Come back later :)"))
                with second_col2:
                    placement = st.selectbox("Describe...", options=df["name"])
                    sign = df.loc[df["name"] == placement, "sign"].iloc[0]

                    if st.button("Learn More"):
                        placement_info, zodiac_info = get_more_info(placement, sign)
                        st.write(f"You have a {sign} {placement}")
                        st.write(f"Your {placement.lower()} sign {placement_info} With a {sign.lower()} placement, you have {zodiac_info}")
        else:
            st.warning("⚠️Enter a valid location⚠️")