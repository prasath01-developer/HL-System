const defaultUser = "prasath";
const defaultPass = "8888";

function process() {

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let userError = document.getElementById("userError");
    let passError = document.getElementById("passError");


    userError.innerText = "";
    passError.innerText = "";

    if (username === "" || username !== defaultUser) {
        userError.innerText = "Enter valid username";
        return;
    }

    if (password === "" || password !== defaultPass) {
        passError.innerText = "Enter valid password";
        return;
    }

    alert("Login Successful!");
    
    window.location.href = "/html/home.html";
}