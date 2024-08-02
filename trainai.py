from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd

# Example dataset
data = {
    'is_virtualized': [1, 0, 1, 0, 1],
    'security_process_count': [5, 1, 4, 0, 6],
    'edr_directory_count': [2, 0, 3, 0, 1],
    'ram_size': [1.5, 8, 2, 16, 1],
    'cpu_count': [1, 4, 2, 8, 1],
    'sandbox_likelihood': [80, 20, 70, 10, 90],
    'label': ['Sandbox', 'Regular Environment', 'Sandbox', 'Regular Environment', 'Sandbox']
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Feature columns
X = df[['is_virtualized', 'security_process_count', 'edr_directory_count', 'ram_size', 'cpu_count', 'sandbox_likelihood']]

# Label column
y = df['label']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))
