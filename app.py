import prediction

from flask import Flask, jsonify
from flask_cors import CORS

import database

# import controller
# import algorithm

app = Flask(__name__)
CORS(app)

# -----------------------------
# Start SUMO (Only Once)
# -----------------------------
# try:
#     controller.start_sumo()
# except Exception as e:
#     print("SUMO Start Error:", e)


# -----------------------------
# Home Route
# -----------------------------
@app.route("/")
def home():
    return "AI Traffic Backend Running Successfully"


# -----------------------------
# Live Traffic Data
# -----------------------------
@app.route("/api/live")
def live_data():

    row = database.get_latest()

    if row is None:
        return jsonify({
            "status": "No Data Found"
        })

    response = {
        "id": row[0],
        "step": row[1],
        "EB0": row[2],
        "EB1": row[3],
        "EB2": row[4],
        "SB0": row[5],
        "SB1": row[6],
        "SB2": row[7],
        "phase": row[8],
        "reward": row[9]
    }

    return jsonify(response)


# -----------------------------
# Q Table
# -----------------------------
# @app.route("/api/qtable")
# def qtable():

#     return jsonify(
#         str(algorithm.get_q_table())
#     )


# -----------------------------
# Close SUMO
# -----------------------------
@app.route("/api/close")
def close():

    return jsonify({
        "status": "Close API Disabled"
    })


# -----------------------------
# History Data (for charts)
# -----------------------------
@app.route("/api/history")
def history():
    rows = database.get_history(100)  # last 100 steps
    result = []
    for row in rows:
        result.append({
            "id":     row[0],
            "step":   row[1],
            "EB0":    row[2],
            "EB1":    row[3],
            "EB2":    row[4],
            "SB0":    row[5],
            "SB1":    row[6],
            "SB2":    row[7],
            "phase":  row[8],
            "reward": row[9]
        })
    return jsonify(result)


# -----------------------------
# Q-Table Data
# -----------------------------
@app.route("/api/qtable")
def qtable():
    rows = database.get_q_table()
    result = []
    for row in rows:
        result.append({
            "state":    row[0],
            "action_0": round(float(row[1]), 4),
            "action_1": round(float(row[2]), 4)
        })
    return jsonify(result)


# -----------------------------
# Simulation Logs
# -----------------------------
@app.route("/api/logs")
def logs():
    rows = database.get_history(50)
    result = []
    for row in rows:
        total_q = row[2] + row[3] + row[4] + row[5] + row[6] + row[7]
        result.append({
            "step":         row[1],
            "phase":        row[8],
            "reward":       row[9],
            "total_queue":  total_q
        })
    return jsonify(result)


# -----------------------------
# Prediction / Forecast
# -----------------------------
@app.route("/api/predict")
def predict():
    try:
        result = prediction.predict_future(n_steps=10)
        if result is None:
            return jsonify({"status": "not_enough_data"})
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000
    )
    
