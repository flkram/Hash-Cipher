from flask import Flask, request, jsonify
from model import load_model, evaluate_password_strength, train_model, create_training_data
import pandas as pd

app = Flask(__name__)

# Load the pre-trained model
model, le = load_model()

# In-memory DataFrame to store password analysis
password_data = pd.DataFrame(columns=['password', 'md5_hash', 'sha256_hash', 'sha3_hash', 'whirlpool_hash', 'strength_prediction'])

# Route to analyze password
@app.route('/analyze_password', methods=['POST'])
def analyze_password():
    data = request.get_json()
    password = data.get('password', '')

    if not password:
        return jsonify({"error": "Password is required"}), 400

    # Evaluate password strength and generate hashes
    md5_hash, sha256_hash, whirlpool_hash, strength = evaluate_password_strength(password, model, le)

    # Save analysis to the in-memory DataFrame
    global password_data
    new_analysis = pd.DataFrame([{
        'password': password,
        'md5_hash': md5_hash,
        'sha256_hash': sha256_hash,
        'whirlpool_hash': whirlpool_hash,
        'strength_prediction': strength
    }])
    password_data = pd.concat([password_data, new_analysis], ignore_index=True)

    return jsonify({
        "password": password,
        "md5_hash": md5_hash,
        "sha256_hash": sha256_hash,
        "whirlpool_hash": whirlpool_hash,
        "strength_prediction": strength
    })

# Route to retrieve password analyses
@app.route('/get_passwords', methods=['GET'])
def get_passwords():
    # Convert DataFrame to a list of dictionaries for easy JSON serialization
    data = password_data.to_dict(orient='records')
    return jsonify(data)

# Route to train the model on password data
@app.route('/train_data', methods=['POST'])
def train_data():
    data = request.get_json()
    passwords = data.get('passwords', [])
    labels = data.get('labels', [])

    if not passwords or not labels:
        return jsonify({"error": "Passwords and labels are required"}), 400

    # Create training data from passwords and labels
    X, y = create_training_data(passwords, labels)
    
    # Train the model
    global model, le
    model, le = train_model(X, y)
    
    # Save the model and label encoder
    model_path = 'password_strength_model.pth'
    encoder_path = 'label_encoder.pkl'
    model.save_model(model, le, model_path, encoder_path)

    return jsonify({"message": "Model training completed"})

#Route to recieve hashed MD5 string
@app.route('/hashMD5', methods=['POST'])
def hash_md5():
    input_str = request.json.get('input')
    if not input_str:
        return jsonify({'error': 'No input string provided'}), 400
    hash_result = lib_hashMD5.hashMD5(input_str.encode('utf-8')).decode('utf-8')
    return jsonify({'hashed_string': hash_result})

#Route to recieve hashed SHA256 string
@app.route('/hashSHA256', methods=['POST'])
def hash_sha256():
    input_str = request.json.get('input')
    if not input_str:
        return jsonify({'error': 'No input string provided'}), 400
    hash_result = lib_hashSHA256.hashSHA256(input_str.encode('utf-8')).decode('utf-8')
    return jsonify({'hashed_string': hash_result})

#Route to recieve hashed SHA3 string
@app.route('/hashSHA3', methods=['POST'])
def hash_sha3():
    input_str = request.json.get('input')
    if not input_str:
        return jsonify({'error': 'No input string provided'}), 400
    hash_result = lib_hashSHA3.hashSHA3(input_str.encode('utf-8')).decode('utf-8')
    return jsonify({'hashed_string': hash_result})

#Route to recieve hashed Whirlpool string
@app.route('/hashWhirlpool', methods=['POST'])
def hash_whirlpool():
    input_str = request.json.get('input')
    if not input_str:
        return jsonify({'error': 'No input string provided'}), 400
    hash_result = lib_hashWhirlpool.hashWhirlpool(input_str.encode('utf-8')).decode('utf-8')
    return jsonify({'hashed_string': hash_result})

#For Flask
if __name__ == '__main__':
    app.run(debug=True)
