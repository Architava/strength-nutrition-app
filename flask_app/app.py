import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'password'),
        database='fitness_db'
    )

def calculate_one_rep_max(weight, reps: int) -> float:
    """Calculates estimated 1RM using the Epley Formula."""
    weight = float(weight) # Cast to float for math operations
    if reps == 1:
        return float(weight)
    return round(weight * (1 + reps / 30.0), 2)

@app.route("/")
def index():
    """Renders the main dashboard template."""
    return render_template("index.html")

@app.route("/api/v1/workouts", methods=["GET", "POST"])
def handle_workouts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        data = request.get_json() or {}
        sql = "INSERT INTO workout_logs (log_date, exercise_name, target_muscle, sets, reps, weight_kg) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (
            data.get("date", datetime.now().strftime("%Y-%m-%d")),
            str(data["exercise"]),
            "Legs", 
            1,
            int(data["reps"]),
            float(data["weight_kg"])
        )
        cursor.execute(sql, val)
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
        
    cursor.execute("SELECT * FROM workout_logs ORDER BY log_date DESC")
    logs = cursor.fetchall()
    
    processed_logs = []
    for log in logs:
        log_copy = log.copy()
        log_copy["weight_kg"] = float(log["weight_kg"]) # Fixes the JSON serialization crash
        log_copy["estimated_1rm"] = calculate_one_rep_max(log["weight_kg"], log["reps"])
        log_copy["log_date"] = log["log_date"].strftime("%Y-%m-%d") if log["log_date"] else None
        processed_logs.append(log_copy)
        
    conn.close()
    return jsonify(processed_logs)

@app.route("/api/v1/nutrition", methods=["POST"])
def handle_nutrition():
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql = "INSERT INTO nutrition_logs (log_date, meal_name, kilocalories, protein_g, carbs_g, fats_g, is_vegetarian) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (
        data.get("date", datetime.now().strftime("%Y-%m-%d")),
        data.get("meal_name", "High Protein Meal"),
        int(data["kilocalories"]),
        float(data["protein_g"]),
        float(data["carbs_g"]),
        float(data["fats_g"]),
        data.get("is_vegetarian", True) 
    )
    cursor.execute(sql, val)
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route("/api/v1/analytics/summary", methods=["GET"])
def analytics_summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM workout_logs")
    total_workouts = cursor.fetchone()["total"]
    
    cursor.execute("SELECT AVG(kilocalories) as avg_kcal FROM nutrition_logs")
    avg_kcal_row = cursor.fetchone()
    avg_kcal = round(float(avg_kcal_row["avg_kcal"]), 1) if avg_kcal_row["avg_kcal"] else 0
    
    cursor.execute("SELECT exercise_name, weight_kg, reps, log_date FROM workout_logs")
    all_workouts = cursor.fetchall()
    
    highest_1rm = 0.0
    max_1rm_entry = None
    
    for log in all_workouts:
        e1rm = calculate_one_rep_max(float(log["weight_kg"]), log["reps"]) # Ensure float here as well
        if e1rm > highest_1rm:
            highest_1rm = e1rm
            max_1rm_entry = {
                "exercise": log["exercise_name"],
                "estimated_1rm": e1rm,
                "date": log["log_date"].strftime("%Y-%m-%d") if log["log_date"] else None
            }
            
    conn.close()
    return jsonify({
        "total_workout_sessions": total_workouts,
        "average_daily_kilocalories": avg_kcal,
        "peak_performance": max_1rm_entry
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)