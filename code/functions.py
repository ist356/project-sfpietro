from datetime import datetime as dt
import requests
import pandas as pd
import time
import pytz


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

def reverse_geocode(lat, lon):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    key = "AIzaSyCdK_LnVQJP38czFSecByjDHhQtZxoZ-x4" 
    params ={"latlng": f"{lat},{lon}", "key": key}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Geocoding API error: {response.status_code}")
        return None, None
    data = response.json()
    if data['status'] != "OK":
        print(f"Geocoding API returned status:{data.get('status')}")
        return None, None

    city = None
    nation = None
    for item in data['results'][0]['address_components']:
        if 'locality' in item['types']: #city
            city = item['long_name']
        if 'country' in item['types']: #country
            nation = item['long_name']
    return city, nation

def get_timezone(city, nation):
    '''
    get timezone from city & nation input
    '''
    url = "https://maps.googleapis.com/maps/api/timezone/json"
    key = "AIzaSyCdK_LnVQJP38czFSecByjDHhQtZxoZ-x4" 
    timestamp = int(time.time()) #current time
    params = {"location":f"{lat},{lon}", "timestamp": timestamp, "key": key}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"HTTP error: {response.status_code}")
        return None
    data = response.json()
    if data['status'] != "OK":
        print(f"Timezone API returned status:{data.get('status')}")
        return None
    
    timezone_id = data.get("timeZoneId", "Unknown Time Zone")
    #print(f"timeZoneId")
    tz = pytz.timezone(timezone_id)
    now = dt.now(tz)
    timezone = now.strftime('%Z')
    return timezone

def get_birth_chart_data(name, date, time, lat, lon, city, nation, timezone):
    '''
    Get birth chart data from API based on user inmput
    '''
    birth_date = dt.strptime(date, "%Y-%m-%d").date()
    birth_time = dt.strptime(time, "%H:%M").time()
    #birth_place = "Boston"
    #birth_country = "America"
    #timezone = "EST"
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
            "city": city,
            "nation": nation,
            "timezone": timezone,
            "zodiac_type": "Tropic"
        }
    }
    headers = {"x-rapidapi-key": key, "x-rapidapi-host": host, "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        #print(response.json())
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def process_birth_chart(raw_data):
    '''
    process data to get each placement
    '''
    data = raw_data['data']
    planets = {key: value for key, value in data.items() if key in [
        'sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto'
        ]}
    houses = {key: value for key, value in data.items() if 'house' in key}

    planets_df = pd.DataFrame.from_dict(planets, orient='index')
    houses_df = pd.DataFrame.from_dict(houses, orient='index')

    aspects = raw_data.get('aspects',{})
    aspects_df = pd.DataFrame.from_dict(aspects)

    return planets_df, houses_df, aspects_df


def get_big_three(raw_data, chart):
    '''
    find star sign from birth chart data
    '''
    sun_sign = planets_df.loc[planets_df['name'] == 'Sun', 'sign'].values[0]
    moon_sign = planets_df.loc[planets_df['name'] == 'Moon', 'sign'].values[0]
    rising_sign = raw_data.get('data',{}).get('first_house', {}).get('sign', 'Unkown')

    big_three = {
        f"Sun: {sun_sign}",
        f"Moon: {moon_sign}",
        f"Rising: {rising_sign}"
    }
    return big_three

def get_horoscope_data(sign):
    '''
    fetch daily horoscope for sign
    '''
    pass

if __name__ == "__main__":
    '''
    name = "Maggy"
    birth_date = "1968-12-17"
    birth_time = "3:00"
    birth_place = "Maryland"
    '''
    name = "Sofia"
    birth_date = "2004-09-19"
    birth_time = "11:11"
    birth_place = "Boston"

    lat, lon = get_lat_lon(birth_place)
    if lat and lon:
        city, nation = reverse_geocode(lat,lon)
        if city and nation:
            timezone = get_timezone(lat, lon)
            #print(f"Latitude: {lat}, Longitude: {lon}, City: {city}, Nation: {nation}, Timezone: {timezone}")
            raw = get_birth_chart_data(name, birth_date, birth_time, lat, lon, city, nation, timezone)
            #print(raw)
            if raw and 'data' in raw:
                planets_df, houses_df, aspects_df = process_birth_chart(raw)
                '''
                print("Planets Data:")
                print(planets_df)
                print("\nHouses Data:")
                print(houses_df)
                print("\nAspects Data:")
                print(aspects_df)
                '''
                #print(planets_df)
                big_three = get_big_three(raw, planets_df)
                print(big_three)
            else:
                print("Invalid or empty response")
    else:
        print("Could not fetch data")
