from datetime import datetime as dt
import plotly.express as px
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

def get_timezone(lat, lon):
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
    url = "https://astrologer.p.rapidapi.com/api/v4/birth-chart"
    key = "fee9b48bc8mshf7ffdb8d9a08daap14d36bjsn4ee22ef704f9"
    host = "astrologer.p.rapidapi.com"
    payload = {
        "subject": {
            "name": name,
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "hour": time.hour,
            "minute": time.minute,
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
    sign_translation = {
        "Ari": "Aries",
        "Tau": "Taurus",
        "Gem": "Gemini",
        "Can": "Cancer",
        "Leo": "Leo",
        "Vir": "Virgo",
        "Lib": "Libra",
        "Sco": "Scorpio",
        "Sag": "Sagittarius",
        "Cap": "Capricorn",
        "Aqu": "Aquarius",
        "Pis": "Pisces"
    }

    data = raw_data['data']
    planets = {key: value for key, value in data.items() if key in [
        'sun','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto'
        ]}
   #houses = {key: value for key, value in data.items() if 'house' in key}

    planets_df = pd.DataFrame.from_dict(planets, orient='index')
    planets_df['sign'] = planets_df['sign'].replace(sign_translation)
    #houses_df = pd.DataFrame.from_dict(houses, orient='index')
    #aspects = raw_data.get('aspects',{})
    #aspects_df = pd.DataFrame.from_dict(aspects)

    return planets_df #, houses_df, aspects_df


def get_big_three(raw_data, chart):
    '''
    find star sign from birth chart data
    '''
    sign_translation = {
        "Ari": "Aries",
        "Tau": "Taurus",
        "Gem": "Gemini",
        "Can": "Cancer",
        "Leo": "Leo",
        "Vir": "Virgo",
        "Lib": "Libra",
        "Sco": "Scorpio",
        "Sag": "Sagittarius",
        "Cap": "Capricorn",
        "Aqu": "Aquarius",
        "Pis": "Pisces"
    }
    zodiac_emojis = {
                     "Aries":       "♈️", 
                     "Taurus":      "♉️", 
                     "Gemini":      "♊️", 
                     "Cancer":      "♋️", 
                     "Leo":         "♌️", 
                     "Virgo":       "♍️", 
                     "Libra":       "♎️", 
                     "Scorpio":     "♏️", 
                     "Sagittarius": "♐️", 
                     "Capricorn":   "♑️", 
                     "Aquarius":    "♒️", 
                     "Pisces":      "♓️"
    }
    sun_sign = chart.loc[chart['name'] == 'Sun', 'sign'].values[0]
    moon_sign = chart.loc[chart['name'] == 'Moon', 'sign'].values[0]
    rising_sign = raw_data.get('data',{}).get('first_house', {}).get('sign', 'Unkown')
    rising_sign = sign_translation.get(rising_sign, rising_sign)

    big_three = {
        "sun" :   sun_sign + zodiac_emojis[sun_sign],
        "moon":   moon_sign + zodiac_emojis[moon_sign],
        "rising": rising_sign + zodiac_emojis[rising_sign]
    }
    return big_three

def get_horoscope_data(sign):
    '''
    fetch daily horoscope for sign
    '''
    url = "https://daily-horoscope-api.p.rapidapi.com/api/Daily-Horoscope-English/"
    querystring = {"zodiacSign":sign,"timePeriod":"weekly"}
    headers = {
        "x-rapidapi-key": "fee9b48bc8mshf7ffdb8d9a08daap14d36bjsn4ee22ef704f9",
        "x-rapidapi-host": "daily-horoscope-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        horoscope = response.json()
        if horoscope.get("status"):
            reading = horoscope.get("prediction", "No avaliable horoscope")
            return reading
    else:
        print("boo")
        return None
    
def get_more_info(placement, sign):
    placements_dict = { 
    "Sun":"represents your core identity, ego, and main essence. It defines the fundamental aspects of your personality and how you express yourself.", 
    "Moon": "represents your emotional self, instincts, and subconscious. It influences your feelings, moods, and how you nurture yourself and others.", 
    "Mercury": "represents communication, intellect, and thought processes. It governs how you express yourself, learn, and analyze information.", 
    "Venus": "represents love, beauty, and relationships. It influences how you approach romance, friendships, and aesthetics.", 
    "Mars": "represents energy, drive, and aggression. It governs how you assert yourself, pursue goals, and handle conflict.", 
    "Jupiter": "represents expansion, growth, and luck. It influences your philosophy, morals, and approach to opportunities.", 
    "Saturn": "represents structure, discipline, and responsibility. It governs lessons, limitations, and how you approach long-term goals.", 
    "Uranus": "represents innovation, rebellion, and individuality. It influences your approach to change and how you break away from traditions.", 
    "Neptune": "represents dreams, intuition, and spirituality. It governs your imagination and connection to the mystical aspects of life.", 
    "Pluto": "represents transformation, power, and rebirth. It governs deep changes, personal growth, and hidden truths."
    } 
    zodiac_traits = {
    "Aries": "courageous, confident, and energetic traits. You're known for being a natural leader and having a strong sense of adventure.", 
    "Taurus": "reliable, practical, and grounded traits. You love stability, comfort, and the finer things in life.", 
    "Gemini": "adaptable, curious, and communicative traits. You thrive on intellectual stimulation and social interaction.", 
    "Cancer": "nurturing, intuitive, and protective traits. You are strongly connected to emotions and home life.", 
    "Leo": "creative, charismatic, and generous traits. You draw attention and love to inspire others.", 
    "Virgo": "detail-oriented, analytical, and hardworking traits. You value practicality and are dedicated to helping others.", 
    "Libra": "diplomatic, charming, and fair-minded traits. You strive for balance and harmony in all aspects of life.", 
    "Scorpio": "passionate, resourceful, and mysterious traits. You are deeply connected to transformation and intense emotions.",
    "Sagittarius": "optimistic, adventurous, and independent traits. You crave freedom and thrive on exploration.", 
    "Capricorn": "ambitious, disciplined, and patient traits. You are focused on achieving long-term success and building a solid foundation.", 
    "Aquarius": "innovative, humanitarian, and independent traits. You think outside the box and value progress.", 
    "Pisces": "compassionate, artistic, and intuitive traits. You are deeply connected to emotions and creativity." 
    }

    #placement = "Sun"
    #sign = "Virgo"
    sign = sign.strip()
    placement = placement.strip()
    placement_info = placements_dict[placement]
    zodiac_info = zodiac_traits[sign]
    return placement_info, zodiac_info

def plot_scatter(df):
    rainbow = px.colors.qualitative.Plotly
    fig = px.scatter(
        df,
        x="sign",
        y="name",
        color="name",
        color_discrete_sequence=rainbow,
        size=None,
        hover_data=["position"],
        title="Planets Placements in Zodiac Signs",
        labels={"name": "Planet", "sign": "Zodiac Sign"}
    )
    return fig

def plot_pie_chart(df):
    element_colors = { "Water": '#304D79', "Air": '#7d9696', "Earth": '#1C5034', "Fire":'#7F3C3C' }
    fig = px.pie(
        df,
        names="sign",
        title="Distribution of Planet Signs",
        color = "element",
        color_discrete_map=element_colors
    )
    return fig

if __name__ == "__main__":

    name = "Sofia"
    birth_date_str = "2004-09-19"
    birth_time_str = "11:11"
    birth_place = "Paris"
    birth_date = dt.strptime(birth_date_str, "%Y-%m-%d").date()
    birth_time = dt.strptime(birth_time_str, "%H:%M").time()

    lat, lon = get_lat_lon(birth_place)
    if lat and lon:
        city, nation = reverse_geocode(lat,lon)
        if city and nation:
            timezone = get_timezone(lat, lon)
            print(f"Latitude: {lat}, Longitude: {lon}, City: {city}, Nation: {nation}, Timezone: {timezone}")
            raw = get_birth_chart_data(name, birth_date, birth_time, lat, lon, city, nation, timezone)
            #print(raw)
            if raw and 'data' in raw:
                planets_df = process_birth_chart(raw)
                print("Planets Data:")
                print(planets_df)
                print("\nHouses Data:")
                print(houses_df)
                print("\nAspects Data:")
                print(aspects_df)
                #print(planets_df)
                big_three = get_big_three(raw, planets_df)
                #print(big_three)
                main_sign = big_three['sun']
                print("HOROSCOPE\n")
                #print(main_sign)
                print(get_horoscope_data(main_sign))
            else:
                print("Invalid or empty response")
    else:
        print("Could not fetch data")

'''
THINGS TO DO:
- finish debugging
- add picture
- THATS IT
'''