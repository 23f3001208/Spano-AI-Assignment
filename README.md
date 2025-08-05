# Nutrition Tracker Backend API

A Flask-based backend application for tracking user nutrition, calculating BMR (Basal Metabolic Rate), and logging meals with nutritional information.

## Features

- User registration with BMR calculation
- Meal logging with nutrition tracking
- Date-based meal history retrieval
- User nutrition status monitoring
- WhatsApp-like webhook for meal logging
- Data persistence using JSON files
- Input validation and error handling

## Requirements

- Python 3.7+
- Flask 2.3.3
- Werkzeug 2.3.7

## Installation and Setup

1. **Clone or download the project files**

   ```bash
   git clone <repository-url>
   cd nutrition-tracker
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check

- **URL**: `GET /`
- **Description**: Check if the API is running
- **Response**: List of available endpoints

### 2. User Registration

- **URL**: `POST /register`
- **Description**: Register a new user and calculate BMR
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "age": 25,
    "weight": 70,
    "height": 175,
    "gender": "male",
    "goal": "weight_loss"
  }
  ```
- **Response**: User data with calculated BMR
- **Validation**: All fields required, valid ranges for age/weight/height

### 3. Log Meals

- **URL**: `POST /log_meals`
- **Description**: Log a meal for a user
- **Request Body**:
  ```json
  {
    "user": "John Doe",
    "meal": "lunch",
    "items": ["Jeera Rice", "Dal", "Cucumber"]
  }
  ```
- **Response**: Logged meal with nutrition information
- **Valid meal types**: breakfast, lunch, dinner, snack

### 4. Get User Meals

- **URL**: `GET /meals/<user>`
- **Description**: Get all meals logged by a user
- **Response**: List of all user's meals

### 5. Get User Meals by Date

- **URL**: `GET /meals/<user>/<date>`
- **Description**: Get user's meals for a specific date
- **Date format**: YYYY-MM-DD
- **Example**: `GET /meals/John%20Doe/2024-01-15`

### 6. User Nutrition Status

- **URL**: `GET /status/<user>`
- **Description**: Get user's nutrition summary
- **Response**:
  - BMR and goal
  - Total nutrition consumed (all time)
  - Today's nutrition
  - Meal counts

### 7. WhatsApp-like Webhook

- **URL**: `POST /webhook`
- **Description**: Log meals using natural language
- **Request Body**:
  ```json
  {
    "user": "John Doe",
    "message": "log lunch: Jeera Rice, Dal"
  }
  ```
- **Message format**: `log [meal_type]: [food1, food2, ...]`

### 8. Food Database

- **URL**: `GET /food_db`
- **Description**: Get all available food items and their nutrition values

## Food Database

The application includes a static food database with the following items:

| Food Item     | Calories | Protein (g) | Carbs (g) | Fiber (g) |
| ------------- | -------- | ----------- | --------- | --------- |
| Jeera Rice    | 250      | 5           | 45        | 2         |
| Dal           | 180      | 12          | 20        | 5         |
| Cucumber      | 16       | 1           | 4         | 1         |
| Roti          | 120      | 3           | 25        | 3         |
| Chicken Curry | 300      | 25          | 8         | 1         |
| Paneer        | 265      | 18          | 6         | 0         |
| Salad         | 25       | 2           | 5         | 3         |
| Rice          | 205      | 4           | 45        | 1         |

## BMR Calculation Formula

The application uses the Mifflin-St Jeor Equation:

- **Men**: BMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
- **Women**: BMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.33 × age in years)

## Data Storage

- Data is stored in JSON files (`users.json` and `meals.json`)
- Files are created automatically when first user registers or meal is logged
- Data persists between application restarts

## Example Usage

### 1. Register a User

```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rahul",
    "age": 28,
    "weight": 75,
    "height": 180,
    "gender": "male",
    "goal": "muscle_gain"
  }'
```

### 2. Log a Meal

```bash
curl -X POST http://localhost:5000/log_meals \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Rahul",
    "meal": "lunch",
    "items": ["Jeera Rice", "Dal", "Cucumber"]
  }'
```

### 3. Check User Status

```bash
curl http://localhost:5000/status/Rahul
```

### 4. Use Webhook

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Rahul",
    "message": "log dinner: Roti, Chicken Curry, Salad"
  }'
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data or missing required fields
- **404 Not Found**: User not found or invalid endpoint
- **405 Method Not Allowed**: Wrong HTTP method used
- **409 Conflict**: User already exists during registration
- **500 Internal Server Error**: Server-side errors

## Input Validation

- **Age**: Must be between 1 and 150 years
- **Weight**: Must be between 1 and 500 kg
- **Height**: Must be between 1 and 300 cm
- **Gender**: Must be 'male' or 'female'
- **Meal types**: Must be breakfast, lunch, dinner, or snack
- **Food items**: Must be a non-empty array

## Project Structure

```
nutrition-tracker/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── users.json         # User data (created automatically)
└── meals.json         # Meal logs (created automatically)
```

## Future Enhancements

- Database integration (PostgreSQL/MySQL)
- User authentication and authorization
- Real WhatsApp integration
- Meal recommendation system
- Advanced nutrition analysis
- Daily/weekly/monthly reports
- Recipe suggestions based on goals

## Troubleshooting

1. **Port already in use**: Change the port in `app.py` (line: `app.run(debug=True, host='0.0.0.0', port=5000)`)
2. **JSON decode error**: Ensure request body is valid JSON
3. **User not found**: Register user first before logging meals
4. **Permission denied**: Ensure write permissions in the application directory

## Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is created for educational purposes as part of the Spano AI assignment.
