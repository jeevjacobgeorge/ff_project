import os
import json
import googlemaps
from geopy.geocoders import Nominatim
from django.shortcuts import render
from django.http import JsonResponse
from folium.plugins import MarkerCluster
import folium
import dotenv
from dotenv import load_dotenv
# Load environment variables
env = dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GMAP_API_KEY = os.getenv('GMAP_API_KEY')
if not GMAP_API_KEY:
    print("Google Maps API key not found. Please set the GMAP_API_KEY environment variable.")
else:
      print(GMAP_API_KEY)
# Google Maps API setup
gmaps = googlemaps.Client(key=GMAP_API_KEY)
geolocator = Nominatim(user_agent="bus_stop_locator")

# Coordinates bounds for South India (customize as needed)
SOUTH_INDIA_LAT_MIN = 8.0
SOUTH_INDIA_LAT_MAX = 14.0
SOUTH_INDIA_LON_MIN = 76.0
SOUTH_INDIA_LON_MAX = 82.0

# Path to your geocoded stops JSON file
GEO_CACHE_FILE = 'geocoded_stops.json'


# Function to check if coordinates are within South India region
def is_in_south_india(latitude, longitude):
    return (SOUTH_INDIA_LAT_MIN <= latitude <= SOUTH_INDIA_LAT_MAX) and \
           (SOUTH_INDIA_LON_MIN <= longitude <= SOUTH_INDIA_LON_MAX)


# Function to load cached geocoded data from a JSON file
def load_geocoded_data():
    try:
        with open(GEO_CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Function to save updated geocoded data back to the cache file
def save_geocoded_data(cached_data):
    with open(GEO_CACHE_FILE, 'w') as f:
        json.dump(cached_data, f, indent=4)


# Function to geocode a bus stop, first checking the cache, then using Nominatim or Google Maps API
def geocode_stop_name(stop_name, cached_data):
    # Check if the stop is in cached data
    if stop_name in cached_data:
        print(f"Using cached data for {stop_name}")
        return cached_data[stop_name]['latitude'], cached_data[stop_name]['longitude']

    try:
        # Attempt geocoding using Nominatim (OpenStreetMap)
        location = geolocator.geocode(stop_name)
        if location and is_in_south_india(location.latitude, location.longitude):
            print(f"Geocoded {stop_name} using Nominatim")
            cached_data[stop_name] = {'latitude': location.latitude, 'longitude': location.longitude}
            save_geocoded_data(cached_data)
            return location.latitude, location.longitude
        else:
            # If Nominatim fails or the location is out of bounds, use Google Maps API
            result = gmaps.geocode(stop_name + ", South India")
            if result:
                print(f"Geocoded {stop_name} using Google Maps API")
                lat = result[0]['geometry']['location']['lat']
                lng = result[0]['geometry']['location']['lng']
                cached_data[stop_name] = {'latitude': lat, 'longitude': lng}
                save_geocoded_data(cached_data)
                return lat, lng
            return None, None
    except Exception as e:
        return None, None


# Function to create a Folium map with bus stops and routes
def create_map(bus_stops):
    if not bus_stops:
        return None  # Return None if there are no bus stops to display

    # Create a Folium map centered on the average location of all bus stops
    map_center = [8.4869, 76.9529]  # Default center, can be changed dynamically
    map = folium.Map(location=map_center, zoom_start=13)

    # Add bus stops to the map with marker clustering
    marker_cluster = MarkerCluster().add_to(map)
    for stop in bus_stops:
        folium.Marker([stop['latitude'], stop['longitude']], popup=stop['name']).add_to(marker_cluster)

    # Connect bus stops with a polyline (route) using Google Maps API
    waypoints = [(stop['latitude'], stop['longitude']) for stop in bus_stops]
    if len(waypoints) < 2:
        return map  # If there are fewer than two stops, no route is drawn

    route = gmaps.directions(
        origin=waypoints[0],
        destination=waypoints[-1],
        waypoints=waypoints[1:-1],
        mode="driving",
    )
    if route:
        route_coords = route[0]['legs'][0]['steps']
        polyline_points = []
        for step in route_coords:
            for point in step['polyline']['points']:
                polyline_points.append([point['lat'], point['lng']])

        folium.PolyLine(polyline_points, color="blue", weight=2.5, opacity=1).add_to(map)

    return map


# View to handle the form, geocode stops, and show the map
def bus_route_view(request):
      
      cached_data = load_geocoded_data()  # Load existing cached geocoded data

      if request.method == 'POST':
            if not GMAP_API_KEY:
                  print("Google Maps API key not found. Please set the GMAP_API_KEY environment variable.")
            else:
                  print(GMAP_API_KEY)
            # Get bus stop names from the form
            stop_names = request.POST.get('stop_names')
            bus_stop_names = list(stop_names.split(','))
            bus_stops = []  # Separate list to store geocoded results
            for stop_name in bus_stop_names:
                  lat, lon = geocode_stop_name(stop_name, cached_data)
                  if lat is not None and lon is not None:
                        bus_stops.append({'name': stop_name, 'latitude': lat, 'longitude': lon})
                  else:
                        print(f"Geocoding failed for stop: {stop_name}")

            if not bus_stops:
                  # If no valid bus stops were found, display an error message
                  return render(request, 'bus_route/bus_route_form.html', {
                  'error_message': 'No valid bus stops were found. Please try again with different names.'
                  })

            # Create the map with bus stops and route
            map = create_map(bus_stops)
            if not map:
                  # If the map couldn't be created, display an error message
                  return render(request, 'bus_route/bus_route_form.html', {
                  'error_message': 'Not enough bus stops to create a route. At least two stops are required.'
                  })

            map_html = map._repr_html_()  # Convert the folium map to HTML for embedding

            return render(request, 'bus_route/bus_route_map.html', {'map_html': map_html})

      return render(request, 'bus_route/bus_route_form.html')

