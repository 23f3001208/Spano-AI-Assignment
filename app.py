from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
import re

app = Flask(__name__)

users_db = {}
meals_db = []

food_db = {
    "Jeera Rice": {"calories": 250, "protein": 5, "carbs": 45, "fiber": 2},
    "Dal": {"calories": 180, "protein": 12, "carbs": 20, "fiber": 5},
    "Cucumber": {"calories": 16, "protein": 1, "carbs": 4, "fiber": 1},
    "Roti": {"calories": 120, "protein": 3, "carbs": 25, "fiber": 3},
    "Chicken Curry": {"calories": 300, "protein": 25, "carbs": 8, "fiber": 1},
    "Paneer": {"calories": 265, "protein": 18, "carbs": 6, "fiber": 0},
    "Salad": {"calories": 25, "protein": 2, "carbs": 5, "fiber": 3},
    "Rice": {"calories": 205, "protein": 4, "carbs": 45, "fiber": 1}
}

def save_data():
    """Save data to JSON files"""
    with open('users.json', 'w') as f:
        json.dump(users_db, f, indent=2)
    with open('meals.json', 'w') as f:
        json.dump(meals_db, f, indent=2, default=str)

def load_data():
    """Load data from JSON files"""
    global users_db, meals_db
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                users_db = json.load(f)
        if os.path.exists('meals.json'):
            with open('meals.json', 'r') as f:
                meals_db = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")

def calculate_bmr(gender, weight, height, age):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender.lower() == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender.lower() == "female":
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.33 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")

def validate_user_data(data):
    """Validate user registration data"""
    required_fields = ['name', 'age', 'weight', 'height', 'gender', 'goal']
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field} is required")
    
    if 'age' in data:
        try:
            age = float(data['age'])
            if age <= 0 or age > 150:
                errors.append("Age must be between 1 and 150")
        except ValueError:
            errors.append("Age must be a valid number")
    
    if 'weight' in data:
        try:
            weight = float(data['weight'])
            if weight <= 0 or weight > 500:
                errors.append("Weight must be between 1 and 500 kg")
        except ValueError:
            errors.append("Weight must be a valid number")
    
    if 'height' in data:
        try:
            height = float(data['height'])
            if height <= 0 or height > 300:
                errors.append("Height must be between 1 and 300 cm")
        except ValueError:
            errors.append("Height must be a valid number")
    
    if 'gender' in data and data['gender'].lower() not in ['male', 'female']:
        errors.append("Gender must be 'male' or 'female'")
    
    return errors

def calculate_nutrition(food_items):
    """Calculate total nutrition for given food items"""
    total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
    
    for item in food_items:
        if item in food_db:
            nutrition = food_db[item]
            for nutrient in total_nutrition:
                total_nutrition[nutrient] += nutrition[nutrient]
    
    return total_nutrition

# API Endpoints

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "Nutrition Tracker API is running",
        "endpoints": [
            "POST /register - Register a new user",
            "POST /log_meals - Log a meal",
            "GET /meals/<user> - Get user's meal history",
            "GET /meals/<user>/<date> - Get user's meals for specific date",
            "GET /status/<user> - Get user's nutrition status",
            "POST /webhook - WhatsApp-like webhook for meal logging"
        ]
    })

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        validation_errors = validate_user_data(data)
        if validation_errors:
            return jsonify({"error": "Validation failed", "details": validation_errors}), 400
        
        username = data['name'].strip()
        if username in users_db:
            return jsonify({"error": "User already exists"}), 409
        
        bmr = calculate_bmr(
            data['gender'], 
            float(data['weight']), 
            float(data['height']), 
            float(data['age'])
        )
        
        user_data = {
            "name": username,
            "age": float(data['age']),
            "weight": float(data['weight']),
            "height": float(data['height']),
            "gender": data['gender'].lower(),
            "goal": data['goal'],
            "bmr": round(bmr, 2),
            "registered_at": datetime.now().isoformat()
        }
        
        users_db[username] = user_data
        save_data()
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_data
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/log_meals', methods=['POST'])
def log_meals():
    """Log a meal for a user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['user', 'meal', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        username = data['user'].strip()
        meal_type = data['meal'].strip().lower()
        food_items = data['items']
        
        if username not in users_db:
            return jsonify({"error": "User not found"}), 404
        
        valid_meals = ['breakfast', 'lunch', 'dinner', 'snack']
        if meal_type not in valid_meals:
            return jsonify({"error": f"Meal type must be one of: {valid_meals}"}), 400
        
        if not isinstance(food_items, list) or len(food_items) == 0:
            return jsonify({"error": "Items must be a non-empty array"}), 400
        
        nutrition = calculate_nutrition(food_items)
        
        meal_entry = {
            "userId": username,
            "mealType": meal_type.capitalize(),
            "foodItems": food_items,
            "nutrition": nutrition,
            "loggedAt": datetime.now().isoformat()
        }
        
        meals_db.append(meal_entry)
        save_data()
        
        return jsonify({
            "message": "Meal logged successfully",
            "meal": meal_entry
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/meals/<user>', methods=['GET'])
def get_user_meals(user):
    """Get all meals for a specific user"""
    try:
        if user not in users_db:
            return jsonify({"error": "User not found"}), 404
        
        user_meals = [meal for meal in meals_db if meal['userId'] == user]
        
        return jsonify({
            "user": user,
            "total_meals": len(user_meals),
            "meals": user_meals
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/meals/<user>/<date>', methods=['GET'])
def get_user_meals_by_date(user, date):
    """Get meals for a specific user on a specific date (YYYY-MM-DD)"""
    try:
        if user not in users_db:
            return jsonify({"error": "User not found"}), 404
        
        user_meals = []
        for meal in meals_db:
            if meal['userId'] == user:
                meal_date = meal['loggedAt'][:10]
                if meal_date == date:
                    user_meals.append(meal)
        
        return jsonify({
            "user": user,
            "date": date,
            "total_meals": len(user_meals),
            "meals": user_meals
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status/<user>', methods=['GET'])
def get_user_status(user):
    """Get nutrition status for a user"""
    try:
        if user not in users_db:
            return jsonify({"error": "User not found"}), 404
        
        user_data = users_db[user]
        user_meals = [meal for meal in meals_db if meal['userId'] == user]
        
        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
        
        for meal in user_meals:
            if 'nutrition' in meal:
                for nutrient in total_nutrition:
                    total_nutrition[nutrient] += meal['nutrition'].get(nutrient, 0)
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_meals = []
        today_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
        
        for meal in user_meals:
            meal_date = meal['loggedAt'][:10]
            if meal_date == today:
                today_meals.append(meal)
                if 'nutrition' in meal:
                    for nutrient in today_nutrition:
                        today_nutrition[nutrient] += meal['nutrition'].get(nutrient, 0)
        
        return jsonify({
            "user": user,
            "bmr": user_data['bmr'],
            "goal": user_data['goal'],
            "total_nutrition_consumed": {
                "calories": round(total_nutrition['calories'], 2),
                "protein": round(total_nutrition['protein'], 2),
                "carbs": round(total_nutrition['carbs'], 2),
                "fiber": round(total_nutrition['fiber'], 2)
            },
            "today_nutrition": {
                "date": today,
                "calories": round(today_nutrition['calories'], 2),
                "protein": round(today_nutrition['protein'], 2),
                "carbs": round(today_nutrition['carbs'], 2),
                "fiber": round(today_nutrition['fiber'], 2)
            },
            "total_meals_logged": len(user_meals),
            "meals_today": len(today_meals)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """WhatsApp-like webhook for meal logging"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message'].strip().lower()
        user = data.get('user', 'default_user')
        
        pattern = r'log\s+(breakfast|lunch|dinner|snack):\s*(.+)'
        match = re.match(pattern, message)
        
        if not match:
            return jsonify({
                "error": "Invalid message format. Use: 'log [meal_type]: [food items]'",
                "example": "log lunch: Jeera Rice, Dal, Cucumber"
            }), 400
        
        meal_type = match.group(1)
        food_items_str = match.group(2)
        food_items = [item.strip() for item in food_items_str.split(',')]
        
        if user not in users_db:
            users_db[user] = {
                "name": user,
                "age": 25,
                "weight": 70,
                "height": 170,
                "gender": "male",
                "goal": "maintain",
                "bmr": calculate_bmr("male", 70, 170, 25),
                "registered_at": datetime.now().isoformat()
            }
        
        nutrition = calculate_nutrition(food_items)
        
        meal_entry = {
            "userId": user,
            "mealType": meal_type.capitalize(),
            "foodItems": food_items,
            "nutrition": nutrition,
            "loggedAt": datetime.now().isoformat()
        }
        
        meals_db.append(meal_entry)
        save_data()
        
        return jsonify({
            "message": f"Meal logged successfully for {user}",
            "parsed": {
                "meal_type": meal_type,
                "food_items": food_items,
                "nutrition": nutrition
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/food_db', methods=['GET'])
def get_food_database():
    """Get available food items and their nutrition values"""
    return jsonify({
        "message": "Available food items in database",
        "total_items": len(food_db),
        "food_items": food_db
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    load_data()
    app.run(debug=True, host='0.0.0.0', port=5000)