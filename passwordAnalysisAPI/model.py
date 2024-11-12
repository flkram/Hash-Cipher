import torch
import hashlib
import math
import string
import pandas as pd
import numpy
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Feature extraction function
def password_features(password):
    """Extract features from the password"""
    length = len(password)
    char_types = {
        'lowercase': sum(1 for c in password if c.islower()),
        'uppercase': sum(1 for c in password if c.isupper()),
        'digits': sum(1 for c in password if c.isdigit()),
        'special': sum(1 for c in password if c in string.punctuation)
    }
    entropy = 0
    if length > 0:
        char_set_size = len(set(password))  # Unique characters
        entropy = math.log2(char_set_size) * length
    
    return [length, char_types['lowercase'], char_types['uppercase'],
            char_types['digits'], char_types['special'], entropy]

# Password strength label generator
def password_strength_label(strength_score):
    """Generate a password strength label based on a score (customizable)"""
    if strength_score < 0.3:
        return 'weak'
    elif strength_score < 0.7:
        return 'medium'
    else:
        return 'strong'

# Neural Network Model for Password Strength Classification
class PasswordStrengthModel(torch.nn.Module):
    def __init__(self):
        super(PasswordStrengthModel, self).__init__()
        self.fc1 = torch.nn.Linear(6, 64)  # 6 input features
        self.fc2 = torch.nn.Linear(64, 32)
        self.fc3 = torch.nn.Linear(32, 16)
        self.fc4 = torch.nn.Linear(16, 3)  # Output 3 classes: weak, medium, strong
        self.softmax = torch.nn.Softmax(dim=1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return self.softmax(x)

# Convert password features and labels into DataFrame
def create_training_data(passwords, labels):
    features = [password_features(pw) for pw in passwords]
    return pd.DataFrame(features, columns=['length', 'lowercase', 'uppercase', 'digits', 'special', 'entropy']), labels

# Training the model on password strength data
def train_model(passwords, labels):
    # Convert labels to integers using LabelEncoder
    le = LabelEncoder()
    labels = le.fit_transform(labels)

    # Split data into training and testing
    X_train, X_test, y_train, y_test = train_test_split(passwords, labels, test_size=0.2, random_state=42)

    # Convert to PyTorch tensors
    X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
    X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.long)

    # Initialize and train the model
    model = PasswordStrengthModel()
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 50
    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()

        # Print loss every 10 epochs
        if epoch % 10 == 0:
            print(f'Epoch [{epoch}/{num_epochs}], Loss: {loss.item():.4f}')
    
    # Evaluate the model on the test set
    model.eval()
    with torch.no_grad():
        outputs = model(X_test_tensor)
        _, predicted = torch.max(outputs, 1)
        print(classification_report(y_test_tensor, predicted))

    return model, le

# Save the model and label encoder to disk
def save_model(model, le, model_path='password_strength_model.pth', encoder_path='label_encoder.pkl'):
    torch.save(model.state_dict(), model_path)
    import pickle
    with open(encoder_path, 'wb') as f:
        pickle.dump(le, f)

# Load the model and label encoder
def load_model(model_path='password_strength_model.pth', encoder_path='label_encoder.pkl'):
    model = PasswordStrengthModel()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    import pickle
    with open(encoder_path, 'rb') as f:
        le = pickle.load(f)
    
    return model, le

# Evaluate a password's strength using the trained model
def evaluate_password_strength(password, model, le):
    features = password_features(password)
    input_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)

    predicted_label = le.inverse_transform(predicted.numpy())
    
    # Hash the password using MD5, SHA-256, and Whirlpool
    md5_hash = hashlib.md5(password.encode()).hexdigest()
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    whirlpool_hash = hashlib.new('whirlpool', password.encode()).hexdigest()

    return md5_hash, sha256_hash, whirlpool_hash, predicted_label[0]

