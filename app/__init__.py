from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd


# Implementation for keeping csv file for car specs, and making sql db for adding reviews
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Load car data from the CSV db
CAR_DATA_FILE = "app/Database/all-vehicles-model@public.csv"
def load_car_data():
	car_data = pd.read_csv(CAR_DATA_FILE, delimiter=";")
	return car_data

car_data = load_car_data()

class Review(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	car_id = db.Column(db.String(50), nullable = False)
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
	# Sort the cars alphabetically and year in descending order
	sorted_car_data = car_data[['ID', 'Make', 'Model', 'Year']].sort_values(by=['Make', 'Model', 'Year'], ascending = [True, True, False])
	car_list = sorted_car_data.to_dict(orient='records')
	return jsonify(car_list)

# Route to get car details from CSV
@app.route("/get_car/<int:car_id>", methods = ["GET"])
def get_car(car_id):
	car = car_data[car_data['ID'] == car_id]
	if car.empty:
		return jsonify({"error": "Car not found"}), 404
	return jsonify(car.to_dict(orient='records')[0])

@app.route("/search_cars", methods=["GET"])
def search_cars():
	query = request.args.get("query", "").strip().lower()

	if not query:
		return jsonify([])

	filtered_cars = car_data[
		car_data.apply(
			lambda x: query in str(x['Make']).lower() or
					  query in str(x['Model']).lower() or
					  query in str(x['Year']).lower(), axis=1
		)
	]

	if filtered_cars.empty:
		return jsonify([])

	car_list = filtered_cars[['ID', 'Make', 'Model', 'Year']].to_dict(orient='records')
	return jsonify(car_list)

# Route to add a review
@app.route("/add_review", methods=["POST"])
def add_review():
	data = request.get_json()
	if not all(key in data for key in ("car_id", "username", "rating", "comments")):
		return jsonify({"error" : "Missing data fields"}), 400

	new_review = Review(
		car_id = data["car_id"],
		username = data["username"],
		rating = data["rating"],
		comment = data["comment"]
	)
	db.session.add(new_review)
	db.session.commit()
	return jsonify({"message" : "Review added successfully"}), 201

# Route to fetch reviews for a specific car
@app.route("/get_reviews/<car_id>", methods=["GET"])
def get_reviews(car_id):
	reviews = Review.query.filter_by(car_id=car_id).all()
	review_list = [
		{"username" : r.username, "rating" : r.rating, "comment" : r.comment}
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
