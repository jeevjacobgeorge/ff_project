document.addEventListener("DOMContentLoaded", function() {
    const staffLoginButton = document.getElementById("button2");
    const userMainButton = document.getElementById("button1");

    if (staffLoginButton) {
        staffLoginButton.addEventListener("click", function() {
            window.location.href = "/tracker/staff_login/"; // Redirect to staff login
        });
    }

    if (userMainButton) {
        userMainButton.addEventListener("click", function() {
            window.location.href = "/tracker/user_main/"; // Redirect to user main page
        });
    }
});
