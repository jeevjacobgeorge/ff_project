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

document.addEventListener("DOMContentLoaded", function() {
    const signupButton = document.getElementById("signup-button");

    signupButton.addEventListener("click", (e) =>{
        window.location.href = "/tracker/staff_signup/"; // Redirect to the staff signup page
    });
});


document.addEventListener("DOMContentLoaded", (e) => {
    const loginButton = document.getElementById("login-button");

    loginButton.addEventListener("click", (e) => {
        var email = document.getElementById("email").value;
        var password = document.getElementById("password").value;
        var username = document.getElementById("username").value;
        
        localStorage.setItem('username',username);

           signInWithEmailAndPassword(auth, email, password)
            .then((userCredential) => {
               // Signed in 
             const user = userCredential.user;
             alert('Logined');
             localStorage.setItem('username',username);
             window.location.href = "/tracker/staff_info/";
                    // ...
             })
               .catch((error) => {
               const errorCode = error.code;
                const errorMessage = error.message;

                alert(errorMessage);
             });

    });
});