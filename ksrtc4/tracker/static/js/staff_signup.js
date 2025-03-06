// Your JavaScript code goes here
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getDatabase, ref, push, update } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-database.js";
import { getAuth, createUserWithEmailAndPassword ,signInWithEmailAndPassword} from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

const appsettings = {
    databaseURL: "https://sample-7ef53-default-rtdb.firebaseio.com/"
};

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBwX2pvwgfJX8Ho0j5wKVVxaayyKADeFdE",
  authDomain: "sample-7ef53.firebaseapp.com",
  databaseURL: "https://sample-7ef53-default-rtdb.firebaseio.com",
  projectId: "sample-7ef53",
  storageBucket: "sample-7ef53.appspot.com",
  messagingSenderId: "197922425298",
  appId: "1:197922425298:web:d94499ab1c0462cc99e00b"
};
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);
const auth = getAuth();
const BUSESRef = ref(database, "STAFF DATA");

let dataRef= null;
function pushstaffdata(email, password,service_id,username,phone_no,driving_license_no,depo) {
    if (!dataRef) {
        dataRef = push(BUSESRef); // Store the reference to the bus node if not already set
    }

    update(dataRef, {
        username : username,
        service_id : service_id,
        email : email,
        password : password,
        phone_no : phone_no,
        driving_license_no : driving_license_no,
        depo : depo
    });
}


document.addEventListener("DOMContentLoaded", (e) => {
    const signupButton = document.getElementById("signup-button");

    signupButton.addEventListener("click", (e) => {
        var email = document.getElementById("email").value;
        var password = document.getElementById("password").value;
        var service_id = document.getElementById("service_id").value;
        var username = document.getElementById("username").value;
        var phone_no = document.getElementById("phone_number").value;
        var depo = document.getElementById("depo").value;
        var driving_license_no = document.getElementById("driving_license_no").value;
        
       createUserWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
                // Signed up 
                const user = userCredential.user;
                pushstaffdata(email,password,service_id,username,phone_no,driving_license_no,depo);
                alert('User created');
                localStorage.setItem('username',username);
                window.location.href = "/tracker/staff_info/";
            })
            .catch((error) => {
                const errorCode = error.code;
                const errorMessage = error.message;
                alert(errorMessage);
            });

        });
});
