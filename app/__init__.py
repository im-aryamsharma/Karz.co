from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd


# Implementation for keeping csv file for car specs, and making sql db for adding reviews
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Load car data from the CSV db
CAR_DATA_FILE = "app/Database/Cars_data_2024.csv"
def load_car_data():
	car_data = pd.read_csv(CAR_DATA_FILE, delimiter=",", encoding="ISO-8859-1")
	return car_data

car_data = load_car_data()

class Review(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	company = db.Column(db.String(100), nullable=False)
	car_name = db.Column(db.String(100), nullable=False)
	username = db.Column(db.String(100), nullable = False)
	rating = db.Column(db.Integer, nullable = False)
	comment = db.Column(db.Text, nullable = False)

# Create database tables
with app.app_context():
	db.create_all()

@app.route("/")
def home():
	return render_template("index.html", t="Home")

# Route to get all cars
@app.route("/get_all_cars", methods=["GET"])
def get_all_cars():
	# Sort by company and car name, alphabetically
	sorted_car_data = car_data[['Company Names', 'Cars Names', 'Cars Prices']].sort_values(
		by=['Company Names', 'Cars Names'],
		ascending=[True, True]
	)
	return jsonify(sorted_car_data.to_dict(orient='records'))

# Route to get car details from CSV
@app.route("/get_car/<company>/<car_name>", methods=["GET"])
def get_car(company, car_name):
	car = car_data[
		(car_data["Company Names"] == company) &
		(car_data["Cars Names"] == car_name)
		]
	if car.empty:
		return jsonify({"error": "Car not found"}), 404
	return jsonify(car.to_dict(orient="records")[0])

@app.route("/search_cars", methods=["GET"])
def search_cars():
	query = request.args.get("query", "").strip().lower()

	if not query:
		return jsonify([])

	filtered_cars = car_data[
		car_data.apply(
			lambda x: query in str(x['Company Names']).lower() or
					  query in str(x['Cars Names']).lower() or
					  query in str(x['Cars Prices']).lower(), axis=1
		)
	]

	if filtered_cars.empty:
		return jsonify([])

	car_list = filtered_cars[['Company Names', 'Cars Names', 'Cars Prices']].to_dict(orient='records')
	return jsonify(car_list)

	car_list = filtered_cars[['Company Names', 'Cars Names', 'Cars Prices']].to_dict(orient='records')
	return jsonify(car_list)

# Route to add a review
@app.route("/add_review", methods=["POST"])
def add_review():
	data = request.get_json()
	if not all(key in data for key in ("company", "car_name", "username", "rating", "comment")):
		return jsonify({"error": "Missing data fields"}), 400

	new_review = Review(
		company=data["company"],
		car_name=data["car_name"],
		username=data["username"],
		rating=data["rating"],
		comment=data["comment"]
	)
	db.session.add(new_review)
	db.session.commit()
	return jsonify({"message" : "Review added successfully"}), 201

# Route to fetch reviews for a specific car
@app.route("/get_reviews/<company>/<car_name>", methods=["GET"])
def get_reviews(company, car_name):
	reviews = Review.query.filter_by(company=company, car_name=car_name).all()
	review_list = [
		{"username": r.username, "rating": r.rating, "comment": r.comment}
		for r in reviews
	]
	return jsonify(review_list)

@app.route("/reviews.html")
def reviews():
	return render_template("reviews.html")

@app.route("/car_list.html")
def car_list():
	return render_template("car_list.html")

@app.route("/specs.html")
def specs():
	return render_template("specs.html")

@app.route("/view")
def view():
	return render_template("view.html", t="View Inventory")

@app.route("/register")
def register():
	return render_template("register.html", t="Register")

if __name__ == '__main__':
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run(debug=True)
