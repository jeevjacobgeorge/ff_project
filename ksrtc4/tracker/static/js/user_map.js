import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getDatabase, ref, get } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-database.js";

const appsettings = {
    databaseURL: "https://sample-7ef53-default-rtdb.firebaseio.com/"
};

const app = initializeApp(appsettings);
const database = getDatabase(app);
const BUSESRef = ref(database, "LIST OF BUSES");

// Initialize the map
var map = L.map('map').setView([10.8505, 76.2711], 13);

// Add the OpenStreetMap tiles as the base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let currentBusMarker = null;
let currentUserMarker =null;

var redMarkerIconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png';
function createCustomIcon(iconUrl) {
    return L.icon({
        iconUrl: iconUrl,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0/images/marker-shadow.png',
        iconSize:     [25, 41], // size of the icon
        shadowSize:   [41, 41], // size of the shadow
        iconAnchor:   [12, 41], // point of the icon which will correspond to marker's location
        shadowAnchor: [12, 41], // the same for the shadow
        popupAnchor:  [1, -34] // point from which the popup should open relative to the iconAnchor
    });
}


        // Retrieve location coordinates of a specific bus and display it on the map
        async function getBusLocation(busName) {
            try {
                const snapshot = await get(BUSESRef);
                if (snapshot.exists()) {
                    snapshot.forEach((childSnapshot) => {
                        const busData = childSnapshot.val();
                        if (busData.bus_name === busName) {
                            const latitude = busData.latitude;
                            const longitude = busData.longitude;
                           
                           
                            // Add a marker to the map at the retrieved location
                            if (currentBusMarker) {
                                map.removeLayer(currentBusMarker);
                            }
                            const redMarkerIcon = createCustomIcon(redMarkerIconUrl);

// Create the marker using the red icon
currentBusMarker = L.marker([latitude, longitude], { icon: redMarkerIcon }).addTo(map)
    .bindPopup('Bus Location')
    .openPopup();
    map.setView(currentBusMarker.getLatLng(),20);



    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`)
    .then(response => response.json())
    .then(data => {
        const locationbox = document.getElementById('locationbox'); // Define locationDiv
        if (data.display_name) {
            // Extracting just the name of the place
            const addressComponents = data.display_name.split(', ');
            const placeName_0 = addressComponents[0];
            const placeName_1 = addressComponents[1];
            // const placeName_2 = addressComponents[2];
            // Display the name of the place
            locationbox.style.display = 'block';
            locationbox.innerText = `\n${placeName_0},\n${placeName_1}`; // Change locationDiv to locationbox
            console.log(placeName_0);
        } else {
            locationbox.style.display = 'block';
            locationbox.innerText = "Location not found"; // Change locationDiv to locationbox
        }
    })
    .catch(error => {
        console.error('Error:', error);
        locationbox.style.display = 'block';
        locationbox.innerText = "Error retrieving location"; // Change locationDiv to locationbox
    });
                        }
                    });
                } else {
                    console.log(`No bus data found in the database.`);
                }
            } catch (error) {
                console.error("Error fetching bus data:", error);
            }
        }


var busName = localStorage.getItem('routescheduleid');
console.log(busName);
getBusLocation(busName);
setInterval(() => getBusLocation(busName), 5000);

function getUserLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const userLatLng = L.latLng(position.coords.latitude, position.coords.longitude);
            
            // Add a marker to the map at the user's location
            if (currentUserMarker) {
                map.removeLayer(currentUserMarker);
            }

            var currentUserMarker = L.marker(userLatLng).addTo(map);

            
           
        }, function(error) {
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    alert("User denied the request for Geolocation. Please enable it in your browser settings to continue.");
                    break;
                case error.POSITION_UNAVAILABLE:
                    alert("Location information is unavailable.");
                    break;
                case error.TIMEOUT:
                    alert("The request to get user location timed out.");
                    break;
                case error.UNKNOWN_ERROR:
                    alert("An unknown error occurred.");
                    break;
            }
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}
getUserLocation();
setInterval(() =>getUserLocation(), 90000);