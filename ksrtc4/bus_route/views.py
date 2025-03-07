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
import polyline  # Required for decoding Google Maps encoded polylines

# Load environment variables
env = dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GMAP_API_KEY = os.getenv('GMAP_API_KEY')
if not GMAP_API_KEY:
    print("DEBUG: Google Maps API key not found. Please set the GMAP_API_KEY environment variable.")
else:
    print("DEBUG: GMAP_API_KEY loaded:", GMAP_API_KEY)

# Google Maps API setup
gmaps = googlemaps.Client(key=GMAP_API_KEY)
geolocator = Nominatim(user_agent="bus_stop_locator")

# Coordinates bounds for South India (customize as needed)
SOUTH_INDIA_LAT_MIN = 8.0
SOUTH_INDIA_LAT_MAX = 14.0
SOUTH_INDIA_LON_MIN = 76.0
SOUTH_INDIA_LON_MAX = 82.0

# Path to your geocoded stops JSON file
GEO_CACHE_FILE = 'bus_route/geocoded_stops.json'


# Function to check if coordinates are within South India region
def is_in_south_india(latitude, longitude):
    in_region = (SOUTH_INDIA_LAT_MIN <= latitude <= SOUTH_INDIA_LAT_MAX) and \
                (SOUTH_INDIA_LON_MIN <= longitude <= SOUTH_INDIA_LON_MAX)
    print(f"DEBUG: Checking if ({latitude}, {longitude}) is in South India: {in_region}")
    return in_region


# Function to load cached geocoded data from a JSON file
def load_geocoded_data():
    try:
        with open(GEO_CACHE_FILE, 'r') as f:
            data = json.load(f)
            print("DEBUG: Loaded cached geocoded data.")
            return data
    except FileNotFoundError:
        print("DEBUG: Cache file not found. Starting with empty cache.")
        return {}


# Function to save updated geocoded data back to the cache file
# def save_geocoded_data(cached_data):
#     with open(GEO_CACHE_FILE, 'w') as f:
#         json.dump(cached_data, f, indent=4)
#     print("DEBUG: Saved updated geocoded data to cache.")


# Function to geocode a bus stop, first checking the cache, then using Nominatim or Google Maps API
def geocode_stop_name(stop_name, cached_data):
    # Check if the stop is in cached data
    if stop_name in cached_data:
        print(f"DEBUG: Using cached data for {stop_name}")
        return cached_data[stop_name]['latitude'], cached_data[stop_name]['longitude']
    
    print(f"DEBUG: No cached data found for {stop_name}\n\n")
    return None, None
    # try:
    #     # Attempt geocoding using Nominatim (OpenStreetMap)
    #     print(f"DEBUG: Attempting Nominatim geocoding for {stop_name}")
    #     location = geolocator.geocode(stop_name)
    #     if location and is_in_south_india(location.latitude, location.longitude):
    #         print(f"DEBUG: Geocoded {stop_name} using Nominatim: ({location.latitude}, {location.longitude})")
    #         cached_data[stop_name] = {'latitude': location.latitude, 'longitude': location.longitude}
    #         # save_geocoded_data(cached_data)
    #         return location.latitude, location.longitude
    #     else:
    #         print(f"DEBUG: Nominatim failed or out of bounds for {stop_name}, trying Google Maps API.")
    #         # If Nominatim fails or location is out of bounds, use Google Maps API
    #         result = gmaps.geocode(stop_name + ", South India")
    #         if result:
    #             lat = result[0]['geometry']['location']['lat']
    #             lng = result[0]['geometry']['location']['lng']
    #             print(f"DEBUG: Geocoded {stop_name} using Google Maps API: ({lat}, {lng})")
    #             cached_data[stop_name] = {'latitude': lat, 'longitude': lng}
    #             # save_geocoded_data(cached_data)
    #             return lat, lng
    #         else:
    #             print(f"DEBUG: Google Maps API did not return a result for {stop_name}.")
    #         return None, None
    # except Exception as e:
    #     print(f"DEBUG: Exception while geocoding {stop_name}: {e}")
    #     return None, None
def create_map(bus_stops):
    if not bus_stops or len(bus_stops) < 2:
        print("DEBUG: Not enough bus stops provided to create map.")
        return None

    # Create a Folium map centered on a default location (adjust as needed)
    map_center = [8.4869, 76.9529]
    map = folium.Map(location=map_center, zoom_start=13)
    print(f"DEBUG: Creating map centered at {map_center}")

    # Add numbered markers for each bus stop in order
    marker_cluster = MarkerCluster().add_to(map)
    for index, stop in enumerate(bus_stops, start=1):
        lat = stop['latitude']
        lon = stop['longitude']
        popup_text = f"{index}. {stop['name']}"
        print(f"DEBUG: Adding marker for stop '{stop['name']}' as #{index} at ({lat}, {lon})")
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.DivIcon(html=f"""<div style="font-size: 42pt; color:red"><b>{index}</b></div>""")
        ).add_to(marker_cluster)

    # Divide bus stops into segments of up to 20 stops (with one-stop overlap between segments)
    segment_size = 20
    segments = []
    i = 0
    while i < len(bus_stops):
        # For each segment, include up to segment_size stops
        segment = bus_stops[i:i + segment_size]
        # If not the first segment, ensure continuity by overlapping the first stop with the previous segment's last stop
        if i != 0 and segment:
            segment = [bus_stops[i - 1]] + segment
        segments.append(segment)
        # Move index forward by segment_size - 1 to have an overlap
        i += segment_size - 1

    # Define a cyclic list of colors for the route segments
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkgreen', 'darkpurple', 'pink']

    # For each segment, request directions from Google Maps and add the polyline with a distinct color
    for seg_index, segment in enumerate(segments):
        # Extract latitude/longitude tuples for this segment
        waypoints = [(stop['latitude'], stop['longitude']) for stop in segment]
        if len(waypoints) < 2:
            print(f"DEBUG: Segment {seg_index + 1} has insufficient waypoints.")
            continue

        origin = waypoints[0]
        destination = waypoints[-1]
        intermediate_waypoints = waypoints[1:-1]

        try:
            print(f"DEBUG: Requesting directions for segment {seg_index + 1}: origin {origin}, destination {destination}, waypoints {intermediate_waypoints}")
            route = gmaps.directions(
                origin=origin,
                destination=destination,
                waypoints=intermediate_waypoints,
                mode="driving",
            )
            if route:
                overview_poly = route[0].get('overview_polyline', {}).get('points')
                if overview_poly:
                    print(f"DEBUG: Decoding polyline for segment {seg_index + 1}.")
                    decoded_points = polyline.decode(overview_poly)
                    color = colors[seg_index % len(colors)]
                    print(f"DEBUG: Drawing segment {seg_index + 1} with color {color}.")
                    folium.PolyLine(decoded_points, color=color, weight=2.5, opacity=1).add_to(map)
                else:
                    print(f"DEBUG: No overview polyline found for segment {seg_index + 1}.")
            else:
                print(f"DEBUG: No route found for segment {seg_index + 1}.")
        except Exception as e:
            print(f"DEBUG: Exception while retrieving route for segment {seg_index + 1}: {e}")

    return map



# View to handle the form, geocode stops, and show the map
def bus_route_view(request):
    print("DEBUG: bus_route_view called with method:", request.method)
    cached_data = load_geocoded_data()  # Load existing cached geocoded data
    print("DEBUG: Cached data loaded:", cached_data)

    if request.method == 'POST':
        # Get bus stop names from the form
        stop_names = request.POST.get('stop_names')
        print("DEBUG: Received stop names from form:", stop_names)
        bus_stop_names = [name.strip() for name in stop_names.split(',')]
        print("DEBUG: Parsed bus stop names:", bus_stop_names)
        bus_stops = []  # List to store geocoded results

        for stop_name in bus_stop_names:
            if stop_name:  # Ensure the stop name is not empty
                print(f"DEBUG: Processing stop name: {stop_name}")
                lat, lon = geocode_stop_name(stop_name, cached_data)
                if lat is not None and lon is not None:
                    print(f"DEBUG: Adding bus stop '{stop_name}' with coordinates: ({lat}, {lon})")
                    bus_stops.append({'name': stop_name, 'latitude': lat, 'longitude': lon})
                else:
                    print(f"DEBUG: Geocoding failed for stop: {stop_name}")

        if not bus_stops:
            # If no valid bus stops were found, display an error message
            print("DEBUG: No valid bus stops were found.")
            return render(request, 'bus_route/bus_route_form.html', {
                'error_message': 'No valid bus stops were found. Please try again with different names.'
            })

        # Create the map with bus stops and route
        map_object = create_map(bus_stops)
        if not map_object:
            print("DEBUG: Map creation failed due to insufficient bus stops.")
            return render(request, 'bus_route/bus_route_form.html', {
                'error_message': 'Not enough bus stops to create a route. At least two stops are required.'
            })

        map_html = map_object._repr_html_()  # Convert the folium map to HTML for embedding
        print("DEBUG: Map created successfully. Rendering map HTML.")
        return render(request, 'bus_route/bus_route_map.html', {'map_html': map_html})

    print("DEBUG: Rendering bus route form.")
    return render(request, 'bus_route/bus_route_form.html')


from django.http import JsonResponse, HttpResponseBadRequest
from .models import Schedule, Route

def get_route_details(request):
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET method is allowed.")
    
    schedule_no = request.GET.get('schedule_no')
    trip_no = request.GET.get('trip_no')

    if not schedule_no or not trip_no:
        return HttpResponseBadRequest("Missing required parameters: schedule_no and trip_no.")
    
    try:
        trip_no = int(trip_no)
    except ValueError:
        return HttpResponseBadRequest("Invalid trip_no parameter. It must be an integer.")
    
    try:
        # Ensure schedule_no is uppercase as per the model's save method.
        schedule = Schedule.objects.get(schedule_no=schedule_no.upper(), trip_no=trip_no)
    except Schedule.DoesNotExist:
        return JsonResponse({"error": "Schedule not found."}, status=404)
    
    # Retrieve all Route objects that match the schedule's route_no, ordered by the sequence number.
    routes = Route.objects.filter(route_no=schedule.route_no.upper()).order_by('order_sequence')
    
    # Prepare the response data with each key as the sequence number.
    data = {}
    for route in routes:
        data[route.order_sequence] = {
            "stop_name": route.stop_name,
            "latitude": route.stop_latitude,
            "longitude": route.stop_longitude,
        }
    
    return JsonResponse(data)
