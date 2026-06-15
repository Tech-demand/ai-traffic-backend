import numpy as np
from sklearn.linear_model import LinearRegression
import database

# --------------------------------
# Train model on historical data
# --------------------------------
def train_model():
    rows = database.get_history(500)

    if len(rows) < 20:
        return None, None

    # Feature: total queue at each step
    queues = [
        row[2] + row[3] + row[4] + row[5] + row[6] + row[7]
        for row in rows
    ]

    # X = window of last 5 queue values, y = next queue value
    WINDOW = 5
    X, y = [], []

    for i in range(WINDOW, len(queues)):
        X.append(queues[i - WINDOW:i])
        y.append(queues[i])

    if len(X) < 10:
        return None, None

    X = np.array(X)
    y = np.array(y)

    model = LinearRegression()
    model.fit(X, y)

    return model, queues


# --------------------------------
# Predict next N steps
# --------------------------------
def predict_future(n_steps=10):
    model, queues = train_model()

    if model is None:
        return None

    WINDOW = 5
    recent = list(queues[-WINDOW:])
    predictions = []

    for _ in range(n_steps):
        x_input = np.array(recent[-WINDOW:]).reshape(1, -1)
        next_val = model.predict(x_input)[0]
        next_val = max(0, round(float(next_val), 2))
        predictions.append(next_val)
        recent.append(next_val)

    # Also return last N actual values for comparison
    actual_recent = [round(float(q), 2) for q in queues[-n_steps:]]

    # Model accuracy score
    WINDOW = 5
    rows = database.get_history(500)
    all_queues = [
        row[2] + row[3] + row[4] + row[5] + row[6] + row[7]
        for row in rows
    ]
    X_all, y_all = [], []
    for i in range(WINDOW, len(all_queues)):
        X_all.append(all_queues[i - WINDOW:i])
        y_all.append(all_queues[i])

    score = round(model.score(np.array(X_all), np.array(y_all)) * 100, 1)

    return {
        "actual":      actual_recent,
        "predicted":   predictions,
        "score":       score,
        "n_steps":     n_steps,
        "status":      "ok"
    }