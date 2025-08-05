from flask import Flask, request, jsonify
from flask_cors import CORS
import ctypes, os
import model
import hashlib
import json

# Run Flask and enable CORS for all routes and origins
app = Flask(__name__)
CORS(app)

# Global hash map for quick lookup
generated_password_hashes = {}

# Load from file if exists
if os.path.exists("outputmaps.json"):
    with open("outputmaps.json", "r") as f:
        generated_password_hashes = json.load(f)

# Creating new default input.txt file
if not os.path.exists("input.txt"):
    default_passwords = [
    "D31lR{(5,m",
    "Px@byJp[@T",
    "Iokw3aL6{k",
    "YD{[Ng>fCy",
    "Y-/GlLe|/h",
    "QZ|B@\\6xDc",
    "z2>`f6vO^f",
    "W8FfdcJ2nU",
    "0<l`*bA[2H",
    "0@om-<w5xu",
    ""
    ]
    with open("input.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(default_passwords))





# Route to check password strength
@app.route('/check_password_strength', methods=['POST'])
def check_password_strength():
    data = request.json
    password = data.get('password', '')

    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    try:
        numSimilar = model.searcher()
        
        return jsonify(numSimilar)
    except:
        if password in ['123456', 'password', 'qwerty', '']:
            return jsonify(2)  # Very common
        elif password in ['welcome1', 'letmein']:
            return jsonify(1)  # Somewhat common
        else:
            return jsonify(0)  # Uncommon
    
        
        





# Route to train the model with JSON data
@app.route('/train_model', methods=['POST'])
def train_model():
    try:
        data = request.json
        # Mock training logic
        if not isinstance(data, dict):
            raise ValueError("Invalid training data format")

        passList = [str(value) for value in data.values()]
        model.addInput(passList)
        
        # Assume training succeeded
        #try:
        model.runner("train")
        #except:
            #return jsonify({"message": "Error uploading training data"})
            
        try:
            model.runner("generate")

            # After password generation, read output.txt and hash the passwords
            if os.path.exists("output.txt"):
                with open("output.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        password = line.strip()
                        hash_val = hashlib.sha256(password.encode()).hexdigest()
                        generated_password_hashes[hash_val] = password

                # Save to JSON
                with open("outputmaps.json", "w", encoding="utf-8") as json_file:
                    json.dump(generated_password_hashes, json_file, indent=4)

        except Exception as e:
            return jsonify({"message": "Error generating passwords from data", "error": str(e)})

            
        return jsonify({"message": "Training data uploaded and processed successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400





# Route to add password to password hash data in JSON file
@app.route("/add_password_hash", methods=["PUT"])
def add_password_hash():
    data = request.get_json()

    password = data.get("password")
    if not password:
        return jsonify({"error": "Password not provided"}), 400

    # Hash the password
    hash_val = hashlib.sha256(password.encode()).hexdigest()

    # Update the global map
    generated_password_hashes[hash_val] = password

    # Save to file
    with open("outputmaps.json", "w", encoding="utf-8") as json_file:
        json.dump(generated_password_hashes, json_file, indent=4)

    return jsonify({"message": "Password and hash saved successfully", "hash": hash_val}), 200





# Route to train the model with JSON data
@app.route('/reset_model', methods=['POST'])
def reset_model():
    model.resetInput()
    return jsonify(0)
        
        
        
        
        
# Route to generate a password
@app.route("/generate_password", methods=["GET"])
def generate_password():
    import random
    import string

    # Mock password generation logic
    password = 'password'
    try:
        password = model.newPassword()
    except:
        password_length = 12
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choices(characters, k=password_length))

    return jsonify({"password": password})





# Route to hash function
@app.route("/hash_text", methods=["POST"])
def hash_text():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Filename not provided'}), 400

    filename = data['filename']
    file_path = os.path.join('../wasmConverters', filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'Algorithm not found'}), 404

    try:
        # Load the shared object file
        wasm_lib = ctypes.CDLL(file_path)

        # Assuming the shared object has a function named 'hash_function'
        if hasattr(wasm_lib, 'hash_function'):
            # Call the 'hash_function' assuming it takes no arguments and returns an integer
            result = wasm_lib.hash_function()
            return jsonify({'result': result}), 200
        else:
            return jsonify({'error': 'hash_function not found in the shared object file'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    

    
# Checks json data to find existing hash    
@app.route("/check_hash", methods=["POST"])
def check_hash():
    data = request.get_json()
    hash_val = data.get("hash", "")

    if not hash_val:
        return jsonify({"error": "Hash not provided"}), 400

    match = generated_password_hashes.get(hash_val)

    if match:
        return jsonify({"found": True, "password": match})
    else:
        return jsonify({"found": False})





# Run app.py as main backend application on port 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)
