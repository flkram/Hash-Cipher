from flask import Flask, request, jsonify
from flask_cors import CORS
import ctypes, os
import model

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins





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
        except:
            return jsonify({"message": "Error generating passwords from data"})
            
        return jsonify({"message": "Training data uploaded and processed successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400





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
    
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)
