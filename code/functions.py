from datetime import datetime as dt
import requests
import pandas as pd
import plotly.express as px
import http.client


def get_lat_lon(location):
    '''
    Get lat and long coordinates from location input
    '''
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    key = "AIzaSyCdK_LnVQJP38czFSecByjDHhQtZxoZ-x4"
    params ={"address": location, "key": key}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            lat = location['lat']
            lon = location['lng']
            return lat, lon
        else:
            print(f"Geocoding Error: {data['status']}")
            return None, None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None, None

def get_birth_chart_data(name, date, time, lat, lon):
    
 ## Get birth chart data from API based on user inmput
    
    birth_date = dt.strptime(date, "%Y-%m-%d").date()
    birth_time = dt.strptime(time, "%H:%M").time()
    birth_place = "Boston"
    birth_country = "America"
    timezone = "EST"
    url = "https://astrologer.p.rapidapi.com/api/v4/birth-chart"
    key = "fee9b48bc8mshf7ffdb8d9a08daap14d36bjsn4ee22ef704f9"
    host = "astrologer.p.rapidapi.com"
    payload = {
        "subject": {
            "name": name,
            "year": birth_date.year,
            "month": birth_date.month,
            "day": birth_date.day,
            "hour": birth_time.hour,
            "minute": birth_time.minute,
            "latitude": lat,
            "longitude": lon,
            "city": birth_place,
            "nation": birth_country,
            "timezone": timezone,
            "zodiac_type": "Tropic"
        }
    }
    headers = {"x-rapidapi-key": key, "x-rapidapi-host": host, "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def process_birth_chart(raw_data):
    '''
    process data to get each placement
    '''
    pass

def get_sign(chart):
    '''
    find star sign from birth chart data
    '''
    pass

def get_horoscope_data(sign):
    '''
    fetch daily horoscope for sign
    '''
    pass

if __name__ == "__main__":
    name = "Sofia"
    birth_date = "2004-09-24"
    birth_time = "11:11"
    birth_place = "Boston MA, USA"

    lat, lon = get_lat_lon(birth_place)
    if lat and lon:
        ##print(f"Latitude: {lat}, Longitude: {lon}")
        raw = get_birth_chart_data(birth_date, birth_time, lat, lon)
        print(raw)
        process_birth_chart(raw)
    else:
        print("Could not retrieve latitude and longitude for given location")
