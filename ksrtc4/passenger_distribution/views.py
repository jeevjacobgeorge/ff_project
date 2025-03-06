import json
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster
from folium import Icon
from geopy.geocoders import Nominatim
from django.shortcuts import render
from django.http import JsonResponse
import sys,os
import dotenv
import requests
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GMAP_API_KEY = os.getenv('GMAP_API_KEY')
# Constants
LIMIT_OF_TOP_BUS_STOPS = 1000
MIN_AVG_THRESHOLD = 1  # At least 31 passengers in 31 days
SOUTH_INDIA_LAT_MIN = 8.0
SOUTH_INDIA_LAT_MAX = 14.0
SOUTH_INDIA_LON_MIN = 76.0
SOUTH_INDIA_LON_MAX = 80.0
GEO_CACHE_FILE = 'passenger_distribution/geocoded_stops.json'  # Update path as needed
FAILURE_CACHE_FILE = 'passenger_distribution/geocoding_failures.json'  # Update path as needed

def call_gemini_api(prompt, api_key):
    """Sends a prompt to the Gemini API and returns the response."""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash") 
    response = model.generate_content(prompt) 

    return response.text

# Set your file paths and parameters
@csrf_exempt 
def ask_gemini(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt') 
        # print("Prompt:", prompt)
        # Call the Gemini API using the prompt and GEMINI_API_KEY
        response = call_gemini_api(prompt, GEMINI_API_KEY) 

        return JsonResponse({'answer': response})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    

def select_month_time(request):
    # Default values for the form
    month = request.GET.get('month', 'October')
    # start_time = int(request.GET.get('start_time', 11))
    # end_time = int(request.GET.get('end_time', 18))
    hours = range(1, 25) 
    days = range(1, 32)
    # Render the page with form
    return render(request, 'passenger_distribution/select_month_time_form.html', {
        'month': month,
        # 'start_time': start_time,
        # 'end_time': end_time,
        'hours': hours,
        'days': days
    })

def geocode_using_gmaps(stop_name, timeout=15):
    # Define the endpoint and parameters for the Google Maps Geocoding API
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': stop_name,  # Address or stop name to be geocoded
        'key': GMAP_API_KEY  # API key for authentication
    }

    try:
        # Make the GET request to the Google Maps API with a timeout
        response = requests.get(endpoint, params=params, timeout=timeout)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # If the API returns results
            if data['status'] == 'OK':
                # Extract latitude and longitude
                lat = data['results'][0]['geometry']['location']['lat']
                lng = data['results'][0]['geometry']['location']['lng']
                return lat, lng
            else:
                print("Geocoding error:", data['status'])
                return None
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print(f"The request timed out after {timeout} seconds.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def generate_bus_stop_map(request):
    print("Generating Bus Stop Map...")
    percent = 0
    month = request.GET.get('month', 'October')  # Default to October
    start_time = int(request.GET.get('start_time', 11))  # Default start time is 11
    end_time = int(request.GET.get('end_time', 18)) 
    file_path = f"passenger_distribution/data/caches/{month}_visualize_airflow.csv"
    
    start_day = request.GET.get('start_day', None)
    end_day = request.GET.get('end_day', None)
    
    # Convert to integers if they exist and are valid
    if start_day:
        start_day = int(start_day) if 1 <= int(start_day) <= 31 else None
    if end_day:
        end_day = int(end_day) if 1 <= int(end_day) <= 31 else None

    # Read the data from the CSV file
    print(f"Reading data from: {file_path}")
    data = pd.read_csv(file_path)
    data["DATE"] = data["DATE_HOUR"].str.split(" ").str[0]
    data["TIME"] = data["DATE_HOUR"].str.split(" ").str[1].astype(int)

    if start_day and end_day:
        data = data[(data["DATE"].str.split("-").str[2].astype(int) >= start_day) & 
                    (data["DATE"].str.split("-").str[2].astype(int) <= end_day)]
    
    data = data[(data["TIME"] >= start_time) & (data["TIME"] <= end_time)]
    total_days = len(data["DATE"].unique())

    top_bus_stops = (
        data.groupby("FROM_STOP_NAME")["TOTAL_PASSENGER"]
        .sum()
        .reset_index()
        .assign(AVERAGE_PASSENGER=lambda x: x["TOTAL_PASSENGER"] / total_days)
        .query("AVERAGE_PASSENGER >= @MIN_AVG_THRESHOLD")
        .sort_values("TOTAL_PASSENGER", ascending=False)
        .head(LIMIT_OF_TOP_BUS_STOPS)
        .to_dict(orient="records")  # Convert to a list of dictionaries
    )

    

    def is_in_south_india(latitude, longitude):
        return (SOUTH_INDIA_LAT_MIN <= latitude <= SOUTH_INDIA_LAT_MAX) and \
               (SOUTH_INDIA_LON_MIN <= longitude <= SOUTH_INDIA_LON_MAX)

    def set_stop_coordinates(stop, latitude, longitude, cached_data, stop_name):
        stop["latitude"] = latitude
        stop["longitude"] = longitude
        cached_data[stop_name] = {"latitude": latitude, "longitude": longitude}

    def handle_failure(stop, stop_name, failures):
        stop["latitude"] = None
        stop["longitude"] = None
        failures.append(stop_name)

    # Load cached data
    def load_geocoded_data():
        try:
            with open(GEO_CACHE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_geocoded_failures():
        try:
            with open(FAILURE_CACHE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    # Save geocoded data and failures
    def save_geocoded_data(data):
        try:
            with open(GEO_CACHE_FILE, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = {}
        existing_data.update(data)
        with open(GEO_CACHE_FILE, 'w') as f:
            json.dump(existing_data, f, indent=4)

    def save_geocoding_failures(failures):
        try:
            with open(FAILURE_CACHE_FILE, 'r') as f:
                existing_failures = json.load(f)
        except FileNotFoundError:
            existing_failures = []
        existing_failures.extend(failures)
        with open(FAILURE_CACHE_FILE, 'w') as f:
            json.dump(existing_failures, f, indent=4)

    # Load cached data
    cached_data = load_geocoded_data()
    cached_failure_data = load_geocoded_failures()
    # Initialize geolocator
    geolocator = Nominatim(user_agent="bus_stop_locator")

    # Prepare data for geocoding (replace with your actual data)
    bus_stops_data = [{"stop_name": row["FROM_STOP_NAME"], "passenger_count": row["AVERAGE_PASSENGER"]} for row in top_bus_stops]

    # Load cached data
    cached_data = load_geocoded_data()
    cached_failure_data = load_geocoded_failures()

    # Initialize counters
    success_count = 0
    failure_count = 0
    failures = []
    total_bus_stops = len(bus_stops_data)
    cache.set('geocoding_progress', 0)
    # Geocode each bus stop
    for i, stop in enumerate(bus_stops_data):
        stop_name = stop["stop_name"]
        percent = (i + 1) / total_bus_stops * 100
        # Skip if already processed
        if stop_name in cached_data:
            stop["latitude"] = cached_data[stop_name]["latitude"]
            stop["longitude"] = cached_data[stop_name]["longitude"]
            success_count += 1
            print_progress_bar(i + 1, len(bus_stops_data))
            continue
        elif stop_name in cached_failure_data:
            failure_count += 1
            print_progress_bar(i + 1, len(bus_stops_data))
            continue

        try:
            # First geocoding attempt
            location = geolocator.geocode(stop_name, timeout=20)
            if location and is_in_south_india(location.latitude, location.longitude):
                set_stop_coordinates(stop, location.latitude, location.longitude, cached_data, stop_name)
                success_count += 1
            else:
                # Retry with gmaps API
                location = geocode_using_gmaps(stop_name+",South India",20)
                if location and is_in_south_india(location.latitude, location.longitude):
                    set_stop_coordinates(stop, location.latitude, location.longitude, cached_data, stop_name)
                    success_count += 1
                else:
                    
                    handle_failure(stop, stop_name, failures)
                    failure_count += 1
        except Exception as e:
            handle_failure(stop, stop_name, failures)
            failure_count += 1
        percent = (i + 1) / total_bus_stops * 100
        cache.set('geocoding_progress', percent)
        # Update progress bar
        print_progress_bar(i + 1, len(bus_stops_data))

    # Save results
    save_geocoded_data(cached_data)
    save_geocoding_failures(failures)

    # Print summary
    print(f"\nGeocoding Successes: {success_count}")
    print(f"Geocoding Failures: {failure_count}")
    if failures:
        print("Failed to geocode the following bus stops:")
        print(failures)
  

    stops_with_coords = [stop for stop in bus_stops_data if 'latitude' in stop and 'longitude' in stop and stop["latitude"] is not None and stop["longitude"] is not None]

    # Convert to Pandas DataFrame for easier handling with Folium
    stops_df = pd.DataFrame(stops_with_coords)

    # Initialize a Folium map centered around an average location
    map_center = [8.4869, 76.9529]
    m = folium.Map(location=map_center, tiles="OpenStreetMap", zoom_start=13, min_zoom=8, max_zoom=18)

    # Logarithmic transformation of passenger counts for better contrast in markers
    stops_df['log_passenger_count'] = np.log1p(stops_df['passenger_count'])
    # print(stops_df)
    # Prepare data for HeatMap using actual passenger counts for intensity
    heat_data = []
    for _, row in stops_df.iterrows():
        heat_data.append([row["latitude"], row["longitude"],  row["passenger_count"]])  # Using actual count for heatmap

    # Create the HeatMap layer with adjusted visual settings
    HeatMap(
        heat_data,
        min_opacity=0.3,  # Set minimum opacity for better visibility (not too faint)
        max_opacity=0.7,  # Set maximum opacity for a more subtle heatmap
        radius=22,        # Adjust radius size to balance between clarity and overlap
        blur=18,          # Moderate blur to avoid excessive smoothing
        gradient={        # Reduced 5-color gradient scale for better distinction
            0.2: 'blue',   # Low density -> blue
            0.4: 'green',  # Medium-low density -> green
            0.6: 'yellow', # Medium-high density -> yellow
            0.8: 'orange', # High density -> orange
            1.0: 'red',    # Very high density -> red
        }
    ).add_to(m)

    # Create a MarkerCluster for the stops (useful for closely spaced stops)
    marker_cluster = MarkerCluster().add_to(m)

    # Define color mapping for passenger counts (using log-transformed values for marker colors)
    def get_marker_color(log_count):
        if log_count < 3.1:   # 0 to 20 passengers
            return 'blue'      # Low density -> blue
        elif log_count < 5.8:  # 21 to 500 passengers
            return 'green'     # Medium density -> green
        elif log_count < 6.9:  # 501 to 1000 passengers
            return 'orange'    # High density -> orange
        else:                  # 1000+ passengers
            return 'red'       # Very high density -> red


    # Add popups and clustered markers for bus stops with their name and transformed passenger count
    for _, row in stops_df.iterrows():
        # Get the color based on the transformed passenger count
        color = get_marker_color(row['log_passenger_count'])

        marker = folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"<b>{row['stop_name']}</b><br>Average Passenger count: {row['passenger_count']:.2f}",
            tooltip=row["stop_name"],
            icon=Icon(color=color, icon="fa-users", prefix="fa"),  # Apply color dynamically
        )
        marker.add_to(marker_cluster)  # Add to MarkerCluster for better organization

    # Create a legend HTML for color decoding (simplified and smaller)
    legend_html = f'''
        <div style="position: fixed;
                    bottom: 50px; left: 30px; width: 250px; height: 160px;
                    background-color: white; border: 2px solid grey; padding: 10px;
                    z-index: 9999; font-size: 10px; border-radius: 8px;">

            <b>Passenger Density Heat Map </b><br>
            <b>Time Range: {start_time}:00 HRS - {end_time}:00 HRS </b> <br>
            <b>Month:{month}</b> <br>
            <i style="background: blue; width: 20px; height: 20px; display: inline-block;"></i> Low Density (0 - 20 passengers)<br>
            <i style="background: green; width: 20px; height: 20px; display: inline-block;"></i> Medium Density (21 - 500 passengers)<br>
            <i style="background: orange; width: 20px; height: 20px; display: inline-block;"></i> High Density (501 - 1000 passengers)<br>
            <i style="background: red; width: 20px; height: 20px; display: inline-block;"></i> Very High Density (1000+ passengers)<br>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    # Generate HTML for the map
    map_html = m._repr_html_()

    data = stops_df.to_dict(orient='records')  # Data is a list of dictionaries
    #remove all latitude and longitude and log_passenger_count
    j = {}
    for d in data:
        j[d['stop_name']] = int(d['passenger_count'])

    print(j)
    # Return the map within a Django template or directly in response
    return render(request, 'passenger_distribution/map_template.html', {'map_html': map_html,'data':json.dumps(j)})


def print_progress_bar(iteration, total, length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(progress * length) - 1)
    spaces = ' ' * (length - len(arrow))
    percent = round(progress * 100, 1)

    sys.stdout.write(f"\r[{arrow}{spaces}] {percent}%")
    sys.stdout.flush()

def get_geocoding_progress(request):
    progress = round(cache.get('geocoding_progress', 0), 2)
    return JsonResponse({"progress": progress})