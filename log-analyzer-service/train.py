import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

print("Creating 100 sample logs for training dataset...")
np.random.seed(42)
templates = [
    ("TimeoutException: Database connection lost after {0}ms", 'High', 0.85),
    ("NullPointerException at AuthController.login line {0}", 'High', 0.90),
    ("DeprecationWarning: backend element {0} is out of date", 'Low', 0.15),
    ("Connection reset by peer while fetching asset {0}", 'Medium', 0.60),
    ("User authentication failed for user_id={0}", 'Medium', 0.55)
]

data = []
for i in range(100):
    tpl, sev, rel_base = templates[np.random.randint(0, len(templates))]
    log_msg = tpl.format(np.random.randint(10, 5000))
    relevance = np.clip(rel_base + np.random.normal(0, 0.05), 0, 1)
    data.append({"log_message": log_msg, "severity": sev, "relevance_score": relevance})

df = pd.DataFrame(data)

X = df['log_message']
y_severity = df['severity']
y_relevance = df['relevance_score']

X_train, X_val, y_sev_train, y_sev_val, y_rel_train, y_rel_val = train_test_split(
    X, y_severity, y_relevance, test_size=0.2, random_state=42
)

print("Vectorizing raw log text features...")
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)

print("Training severity classifier & relevance regressor...")
sev_model = RandomForestClassifier(n_estimators=50, random_state=42)
sev_model.fit(X_train_vec, y_sev_train)

rel_model = RandomForestRegressor(n_estimators=50, random_state=42)
rel_model.fit(X_train_vec, y_rel_train)

print("Packing and exporting model file bundle...")
model_bundle = {
    "vectorizer": vectorizer,
    "severity_model": sev_model,
    "relevance_model": rel_model
}
joblib.dump(model_bundle, "log_analyzer.pkl")
print("Success! 'log_analyzer.pkl' has been generated in your workspace directory.")