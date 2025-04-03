from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timezone

# Implementation for keeping csv file for car specs, and making sql db for adding reviews
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'PpTnRQx3aQzXlKZopNaSaRxU5zlPXTSf'

db = SQLAlchemy(app)

# Load car data from the CSV db
CAR_DATA_FILE = "app/Database/Cars_data_2024.csv"
def load_car_data():
	car_data = pd.read_csv(CAR_DATA_FILE, delimiter=",", encoding="ISO-8859-1")
	return car_data

car_data = load_car_data()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationship to user
    user = db.relationship('User', backref='reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'car_id': self.car_id,
            'user_id': self.user_id,
            'username': self.user.username,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

# Create database tables
with app.app_context():
	db.create_all()

@app.route("/")
def home():
	return render_template("index.html", t="Home")

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Get reviews for a specific car by ID
@app.route("/api/cars/<int:car_id>/reviews", methods=["GET"])
def get_car_reviews(car_id):
    reviews = Review.query.filter_by(car_id=car_id).order_by(Review.created_at.desc()).all()
    return jsonify([review.to_dict() for review in reviews])

# Add a new review (protected endpoint)
@app.route("/api/cars/<int:car_id>/reviews", methods=["POST"])
@login_required
def add_review(car_id):
    data = request.get_json()
    
    # Validate car exists in CSV
    car = car_data[car_data["id"] == car_id]
    if car.empty:
        return jsonify({"error": "Car not found"}), 404
    
    # Validate input
    if not data or 'rating' not in data or 'comment' not in data:
        return jsonify({"error": "Rating and comment are required"}), 400
    
    try:
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except ValueError:
        return jsonify({"error": "Invalid rating format"}), 400
    
    # Create new review
    new_review = Review(
        car_id=car_id,
        user_id=session['user_id'],
        rating=rating,
        comment=data['comment'].strip()
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    return jsonify(new_review.to_dict()), 201

@app.route("/api/check-auth", methods=["GET"])
def check_auth():
	# Check if user_id exists in session
	if 'user_id' in session:
		user = User.query.get(session['user_id'])
		if user:
			return jsonify({
				"authenticated": True,
				"username": user.username
			})
	
	# Return unauthenticated if no session found
	return jsonify({"authenticated": False})

# Logout endpoint
@app.route("/api/logout", methods=["POST"])
def logout():
	session.pop('user_id', None)
	return jsonify({"message": "Logged out successfully"}), 200

# Login API 
@app.route("/api/login", methods=["POST"])
def api_login():
	data = request.get_json()
	
	# Validate required fields
	if not all(key in data for key in ("username", "password")):
		return jsonify({"error": "Username and password are required"}), 400

	# Find user
	user = User.query.filter_by(username=data['username']).first()
	
	# Validate credentials
	if not user or not user.check_password(data['password']):
		return jsonify({"error": "Invalid username or password"}), 401
	
	session['user_id'] = user.id

	return jsonify({
		"message": "Login successful",
		"user": {
			"id": user.id,
			"username": user.username
		}
	}), 200

# Register API
@app.route("/api/register", methods=["POST"])
def api_register():
	data = request.get_json()
	
	# Validate required fields
	if not all(key in data for key in ("username", "password")):
		return jsonify({"error": "Username and password are required"}), 400

	# Check if username exists
	if User.query.filter_by(username=data['username']).first():
		return jsonify({"error": "Username already taken"}), 400

	# Create new user
	user = User(username=data['username'])
	user.set_password(data['password'])
	
	db.session.add(user)
	db.session.commit()

	return jsonify({"message": "Registration successful", "username": user.username}), 201

# Route to get all cars
@app.route("/get_all_cars", methods=["GET"])
def get_all_cars():
	# Sort by company and car name, alphabetically
	sorted_car_data = car_data[['id', 'Company Names', 'Cars Names', 'Cars Prices', 'Image', 'Engine']].sort_values(
		by=['id'],
		ascending=[True]
	)
	
	# Replace "NaN" with None (which becomes null in JSON)
	sorted_car_data['Image'] = sorted_car_data['Image'].fillna('')
	
	# Convert to dictionary and return as JSON
	return jsonify(sorted_car_data.to_dict(orient='records'))

# Route to get car details from CSV
@app.route("/get_car/<id>", methods=["GET"])
def get_car(id):
	car = car_data[car_data["id"] == int(id)]
	if car.empty:
		return jsonify({"error": "Car not found"}), 404
	return jsonify(car.to_dict(orient="records")[0])

@app.route("/reviews.html")
def reviews():
	return render_template("reviews.html")

@app.route("/car_list.html")
def car_list():
	return render_template("car_list.html")

@app.route("/specs")
def specs():
	return render_template("specs.html")

@app.route("/view")
def view():
	return render_template("view.html", t="View Inventory")

@app.route("/register")
def register():
	return render_template("register.html", t="Sign In/Register")

if __name__ == '__main__':
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run(debug=True)
