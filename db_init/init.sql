CREATE DATABASE IF NOT EXISTS fitness_db;
USE fitness_db;

CREATE TABLE nutrition_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_date DATE NOT NULL,
    meal_name VARCHAR(100) NOT NULL,
    kilocalories INT NOT NULL,
    protein_g INT NOT NULL,
    carbs_g INT NOT NULL,
    fats_g INT NOT NULL,
    is_vegetarian BOOLEAN DEFAULT TRUE
);

CREATE TABLE workout_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_date DATE NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    target_muscle VARCHAR(50) NOT NULL,
    sets INT NOT NULL,
    reps INT NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL
);