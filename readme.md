# Hash Cipher

## Overview
Hash Cipher allows users to hash files or text using various cryptographic algorithms, including **SHA256**, **SHA1**, **MD5**, and **Whirlpool**. The application also integrates machine learning algorithms to analyze password security and train AI models based on a list of password data. The backend uses Flask and C++ for hashing, while the frontend provides an interactive experience for users to input data, view results, and interact with password strength analysis.

## Link
- [Website Hosted by GitHub Pages](https://flkram.github.io/Hash-Cipher/).

## Technologies Used

- **C++**: Used for implementing the core cryptographic hashing algorithms (SHA256, SHA1, MD5, Whirlpool). The C++ code is responsible for securely hashing text or files and providing the hashed output.
- **Flask and Python**: Used for backend. Handles user requests such as sending text or files for hashing, password strength analysis, and model training. Reads c++ code by converting it into a .so file
- **PyTorch**: Used to implement machine learning algorithms for password strength analysis. The PyTorch model evaluates password strength based on historical password data and adjusts the analysis over time with additional training data.
- **Pandas**: Utilized for managing and processing the training data (in CSV, JSON, or XLSX formats). It helps in efficiently handling and manipulating password datasets used to train the machine learning model.
- **HTML/CSS/JavaScript**: The frontend is built using standard web technologies like HTML, CSS, and JavaScript to provide an intuitive and responsive interface for users to interact with the application.


## Getting Started and Running the Project

### Frontend

You can access it through the link provided above. You can also access index.html locally after cloning this project.

### Backend

The backend is powered by Flask. To run the backend, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/flkram/Hash-Cipher.git
   cd Hash-Cipher
   ```

2. **Set up the Python environment**:
   - Create a virtual environment (optional but recommended):
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows, use venv\Scripts\activate
     ```
   - Install required dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Build the C++ components** (if applicable):
   - For Linux:
     ```bash
     g++ -o hash_cipher hash_cipher.cpp -lssl -lcrypto
     ```
   - For Windows, use Visual Studio to compile the C++ code.

   - An **alternative** for compiling  the c++ components is using WebAssembly to conver the code into JavaScript. To do this run these commands on bash:
   ```bash
   #Install Emscripten:
    git clone https://github.com/emscripten-core/emsdk.git
    cd emsdk
    Install and activate the latest version:
    Copy code
    ./emsdk install latest
    ./emsdk activate latest
    source ./emsdk_env.sh

    #Compile files to WebAssembly:
    ./wasmConverters/wasmConverter.sh:
    ```
    


4. **Run the Flask server**:
   ```bash
   flask run
   ```

   By default, the Flask server will run at [http://127.0.0.1:5000](http://127.0.0.1:5000).