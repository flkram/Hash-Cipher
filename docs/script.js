let currentAlgorithm = 'SHA-256';
let currentMode = 'text';

function selectAlgorithm(algorithm) {
    // Hide the Train Data container when a new algorithm is selected
    document.getElementById("trainDataContainer").style.display = "none";
    
    currentAlgorithm = algorithm;
    document.getElementById("algoTitle").textContent = `${algorithm} Hasher`;
    document.getElementById("hashOutput").value = ''; // Clear the output area
    showHashContainer();
}

function openStrengthCalculator() {
    // Hide all other containers
    document.getElementById("hashContainer").style.display = 'none';
    document.getElementById("trainDataContainer").style.display = 'none';
    document.getElementById("passwordGeneratorContainer").style.display = 'none';
    
    // Show the Password Strength container
    document.getElementById("strengthContainer").style.display = 'block';
}



// Function to toggle between text and file hashing modes
function toggleMode() {
    if (currentMode === 'text') {
        document.getElementById("textMode").style.display = 'none';
        document.getElementById("fileMode").style.display = 'block';
        document.querySelector("button").textContent = "Switch to Text Mode";
        currentMode = 'file';
    } else {
        document.getElementById("textMode").style.display = 'block';
        document.getElementById("fileMode").style.display = 'none';
        document.querySelector("button").textContent = "Switch to File Mode";
        currentMode = 'text';
    }
    document.getElementById("hashOutput").value = ''; // Clear the output area
}

// Function to hash text input
async function hashText() {
    const text = document.getElementById("textInput").value;
    const encoder = new TextEncoder();
    const data = encoder.encode(text);

    let hashHex = '';
    if (currentAlgorithm === 'SHA-256') {
        const hashBuffer = await crypto.subtle.digest("SHA-256", data);
        hashHex = bufferToHex(hashBuffer);
    } else if (currentAlgorithm === 'SHA-3') {
        hashHex = sha3_256(arrayBufferToHex(data)); // SHA-3 hashing using js-sha3 library
    } else if (currentAlgorithm === 'CRC-32') {
        const hash = CRC32.str(text); // Use the CRC32 library to hash the input text
        hashHex = (hash >>> 0).toString(16);
        if (hashHex == '0') hashHex = '00000000';
    } else if (currentAlgorithm === 'MD5') {
        hashHex = md5(new TextDecoder().decode(data)); // MD5 hashing using blueimp-md5 library
    }

    document.getElementById("hashOutput").value = hashHex;
}

// Function to hash file input
async function hashFile() {
    const fileInput = document.getElementById("fileInput");
    if (fileInput.files.length === 0) {
        alert("Please select a file to hash.");
        return;
    }

    const file = fileInput.files[0];
    const arrayBuffer = await file.arrayBuffer();

    let hashHex = '';
    if (currentAlgorithm === 'SHA-256') {
        const hashBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
        hashHex = bufferToHex(hashBuffer);
    } else if (currentAlgorithm === 'SHA-3') {
        hashHex = sha3_256(arrayBufferToHex(arrayBuffer)); // SHA-3 hashing using js-sha3
    } else if (currentAlgorithm === 'CRC-32') {
        const decodedText = new TextDecoder().decode(new Uint8Array(arrayBuffer)); // Convert Uint8Array to string
        hashHex = CRC32.str(decodedText);
    } else if (currentAlgorithm === 'MD5') {
        hashHex = md5(arrayBufferToHex(arrayBuffer)); // MD5 hashing using blueimp-md5
    }

    document.getElementById("hashOutput").value = hashHex;
}

// Helper function to convert ArrayBuffer to Hexadecimal string
function arrayBufferToHex(buffer) {
    return Array.from(new Uint8Array(buffer))
        .map(byte => byte.toString(16).padStart(2, '0'))
        .join('');
}

// Helper function to convert buffer to hexadecimal string
function bufferToHex(buffer) {
    const hashArray = Array.from(new Uint8Array(buffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}


function showHashContainer() {
    document.getElementById("hashContainer").style.display = 'block';
    document.getElementById("strengthContainer").style.display = 'none';
    document.getElementById("trainDataContainer").style.display = 'none';
    document.getElementById("passwordGeneratorContainer").style.display = 'none';
}


// Function to calculate password strength and check with API
async function calculateStrength() {
    const password = document.getElementById("passwordInput").value;
    const strengthOutput = document.getElementById("strengthOutput");

    // Make an API call to check password strength
    let isDefault = "";
    try{
        const response = await fetch('http://localhost:5000/check_password_strength', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: password })
        });

        const data = await response.json();
        const intResponse = parseInt(data, 10);
        if (intResponse == 0){
            isDefault = "Low usage from training data.\n This password is uncommon\n Number of occurrences: " + intResponse.toString();
        }
        else if (intResponse == 1){
            isDefault = "Medium usage from training data\n This password is somewhat common\n Number of occurrences: " + intResponse.toString();
        }
        else{
            isDefault = "High usage from training data\n This password is very common\n Number of occurrences: " + intResponse.toString() + "+";
        }
    }
    catch (error){
        isDefault =  "(Connect to backend API to add training data. )";
    }


    //---


    let strengthDefault = "Weak";
    
    // Apply default algorithm to determine password strength
    if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password) && /[!@#$%^&*]/.test(password)) {
        strengthDefault = "Strong";
    } else if (password.length >= 6) {
        strengthDefault = "Moderate";
    }

    // Update the output with the default algorithm message and password tips
    strengthOutput.value = ` ${isDefault}\n\n

    Password strength: ${strengthDefault} 

    A strong password:\n` +
                            `    - Has at least 8 characters.\n` +
                            `    - Contains a uppercase and lowercase letter\n` +
                            `    - Includes numbers (e.g., 1, 2, 3).\n` +
                            `    - Uses special characters (e.g., !, @, #, $).`;
}


function downloadStrength() {
    const strengthText = document.getElementById("strengthOutput").value;
    const blob = new Blob([strengthText], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "password_strength.txt";
    link.click();
}

function openTrainData() {
    // Hide all other containers
    document.getElementById("hashContainer").style.display = "none";
    document.getElementById("strengthContainer").style.display = "none";
    document.getElementById("passwordGeneratorContainer").style.display = "none";
    

    // Show the Train Data container
    document.getElementById("trainDataContainer").style.display = "block";
}

async function trainModel() {
    const jsonInput = document.getElementById("jsonInput");
    const errorMessage = document.getElementById("trainError");

    // Clear previous error message
    errorMessage.style.display = "none";
    errorMessage.textContent = "";

    // Validate JSON input
    const jsonData = jsonInput.value.trim();
    if (!jsonData) {
        errorMessage.textContent = "Please enter valid JSON data.";
        errorMessage.style.display = "block";
        return;
    }

    let parsedData;
    try {
        parsedData = JSON.parse(jsonData);
    } catch (error) {
        errorMessage.textContent = "Invalid JSON format. Please check your input.";
        errorMessage.style.display = "block";
        return;
    }

    try {
        const response = await fetch("http://localhost:5000/train_model", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(parsedData),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();
        alert(result.message || "Training data uploaded and processed successfully.");

        // Clear JSON input after successful processing
        jsonInput.value = "";
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message} - backend API`;
        errorMessage.style.display = "block";
    }
}

async function resetModel(){
    try {
        const response = await fetch("http://localhost:5000/reset_model", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();
        alert("Training data successfully reset with status: " + result.toString());

        // Clear JSON input after successful processing
        jsonInput.value = "";
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message} - backend API`;
        errorMessage.style.display = "block";
    }
}
// Show Password Generator and hide other containers
function openPasswordGenerator() {
    document.getElementById("hashContainer").style.display = "none";
    document.getElementById("strengthContainer").style.display = "none";
    document.getElementById("trainDataContainer").style.display = "none";
    document.getElementById("passwordGeneratorContainer").style.display = "block";
}

// Fetch password from backend and display it
async function generatePassword() {
    const passwordOutput = document.getElementById("generatedPassword");

    try {
        const response = await fetch("http://localhost:5000/generate_password", {
            method: "GET",
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const result = await response.json();
        if (result.password){
            passwordOutput.value = result.password;
        }
        else{
            throw new Error();
        }
    } catch (error) {
        const length = Math.floor(Math.random() * 3) + 10; // Random length between 10 and 12
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+[]{}|;:,.<>?";
        
        let password = "";
        for (let i = 0; i < length; i++) {
            const randomIndex = Math.floor(Math.random() * chars.length);
            password += chars[randomIndex];
        }
        
        passwordOutput.value = password;
    }
}







