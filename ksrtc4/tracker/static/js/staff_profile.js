import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getDatabase, ref, push, update ,get } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-database.js";

const appsettings = {
    databaseURL: "https://sample-7ef53-default-rtdb.firebaseio.com/"
};

const app = initializeApp(appsettings);
const database = getDatabase(app);
const BUSESRef = ref(database, "LIST OF BUSES");
const staffdataRef = ref(database, "STAFF DATA");

let busRef = null; // Store reference to the bus node
const bus_id = localStorage.getItem('routescheduleid_staff');
console.log(bus_id);

// Function to push latitude and longitude to Firebase
function pushLocationToFirebase(latitude, longitude) {
    if (!busRef) {
        busRef = push(BUSESRef); // Store the reference to the bus node if not already set
    }

    update(busRef, {
        latitude: latitude,
        longitude: longitude,
        bus_name: bus_id,
        status: "updated3"
    });
}

function UpdateLocation(latitude, longitude) {
    if (busRef) {
        update(busRef, {
            latitude: latitude,
            longitude: longitude,
            status: "updated"
        });
    } else {
        console.error("No bus data found.");
    }
}

let latitude;
let longitude;

function getLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            latitude = position.coords.latitude;
            longitude = position.coords.longitude;

            pushLocationToFirebase(latitude, longitude);
            UpdateLocation(latitude, longitude);
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
getLocation();
setInterval(() => getLocation(), 4000);

async function getstaffdata(username) {
    try {
        const snapshot = await get(staffdataRef);
        if (snapshot.exists()) {
            snapshot.forEach((childSnapshot) => {
                const staff_data = childSnapshot.val();
                if (staff_data.username === username) {
                    const email = staff_data.email;
                    const service_id = staff_data.service_id;
                    const phone_number = staff_data. phone_no;
                    const license_number = staff_data.driving_license_no;
                    const depo = staff_data.depo;

                    const routescheduleid_staff = localStorage.getItem('routescheduleid_staff');
                    const from = localStorage.getItem('from');
                    const to = localStorage.getItem('to');

                    // Update input fields with retrieved data
                    console.log(email)
                    document.getElementById('username').value = username;
                    document.getElementById('email').value = email;
                    document.getElementById('service_id').value = service_id;
                    document.getElementById('phone_number').value = phone_number;
                    document.getElementById('license_number').value = license_number;
                    document.getElementById('depo').value = depo;
                }
            });
            
        } else {
            console.log(`No bus data found in the database.`);
        }
    } catch (error) {
        console.error("Error fetching bus data:", error);
    }
}




const username = localStorage.getItem('username');
getstaffdata(username);