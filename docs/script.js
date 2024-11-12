let currentAlgorithm = 'SHA-256';
let currentMode = 'text';

function selectAlgorithm(algorithm) {
    // Hide the Train Data container when a new algorithm is selected
    document.getElementById("trainDataContainer").style.display = "none";
    
    // Check if the selected algorithm is Whirlpool
    if (algorithm === 'Whirlpool') {
        alert("Whirlpool unable to run on GitHub Pages. Clone locally to run this hashing algorithm.");
        return;
    }
    
    currentAlgorithm = algorithm;
    document.getElementById("algoTitle").textContent = `${algorithm} Hasher`;
    document.getElementById("hashOutput").value = ''; // Clear the output area
    showHashContainer();
}

function openStrengthCalculator() {
    // Hide all other containers
    document.getElementById("hashContainer").style.display = 'none';
    document.getElementById("trainDataContainer").style.display = 'none';
    
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
    } else if (currentAlgorithm === 'Whirlpool') {
        hashHex = whirlpool(data); // Whirlpool hashing (needs to be implemented or use a library)
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
    } else if (currentAlgorithm === 'Whirlpool') {
        hashHex = whirlpool(arrayBuffer); // Whirlpool hashing
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

// Whirlpool hashing function (implement or use a library)
function whirlpool(data) {
    // Assuming you can use a library for Whirlpool, or write your own implementation
    // If using a library, call it here.
    return "Whirlpool hash not implemented"; // Placeholder
}


// Helper function to convert buffer to hexadecimal string
function bufferToHex(buffer) {
    const hashArray = Array.from(new Uint8Array(buffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}


function showHashContainer() {
    document.getElementById("hashContainer").style.display = 'block';
    document.getElementById("strengthContainer").style.display = 'none';
    document.getElementById("trainDataContainer").style.display = 'none';  // Hide Train Data container
}


// Function to calculate password strength and check with API
async function calculateStrength() {
    const password = document.getElementById("passwordInput").value;
    const strengthOutput = document.getElementById("strengthOutput");

    try {
        // Make an API call to check password strength
        const response = await fetch('http://localhost:5000/check_password_strength', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: password })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch password strength');
        }

        const data = await response.json();

        // Display the response from the backend (e.g., 'weak', 'medium', 'strong')
        strengthOutput.value = `Password strength: ${data.strength}`;
    } catch (error) {
        let strengthDefault = "Weak";
        
        // Apply default algorithm to determine password strength
        if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password) && /[!@#$%^&*]/.test(password)) {
            strengthDefault = "Strong";
        } else if (password.length >= 6) {
            strengthDefault = "Moderate";
        }

        // Update the output with the default algorithm message and password tips
        strengthOutput.value = `(Using default algorithm. Connect to backend API to add training data. )

Password strength: ${strengthDefault} 

A strong password:\n` +
                               `    - Has at least 8 characters.\n` +
                               `    - Contains a uppercase and lowercase letter\n` +
                               `    - Includes numbers (e.g., 1, 2, 3).\n` +
                               `    - Uses special characters (e.g., !, @, #, $).`;
    }
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

    // Show the Train Data container
    document.getElementById("trainDataContainer").style.display = "block";
}

// Method to handle training the model
async function trainModel() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        document.getElementById("trainError").style.display = "block";
        document.getElementById("trainError").innerText = "Please select a csv/json/xlsx file with 6 columns";
        return;
    }

    // Check if the file is CSV, XLSX, or JSON and validate it
    if (!['application/json', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(file.type)) {
        document.getElementById("trainError").style.display = "block";
        document.getElementById("trainError").innerText = "ERROR: Invalid file type.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/train_data", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById("trainError").style.display = "none";
            console.log("model.py received data");
            alert("Training successful!");
        } else {
            document.getElementById("trainError").style.display = "block";
            document.getElementById("trainError").innerText = "ERROR: " + data.error;
        }
    } catch (error) {
        document.getElementById("trainError").style.display = "block";
        document.getElementById("trainError").innerText = "ERROR: backend API not connected.";
    }
}



