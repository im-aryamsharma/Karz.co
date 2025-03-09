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
    print("Sample Car IDs", car_data['ID'].head(10))
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
    return render_template("index.html")

# Route to get car details from CSV
@app.route("/get_car/<int:car_id>", methods = ["GET"])
def get_car(car_id):
    car = car_data[car_data['ID'] == car_id]
    if car.empty:
        return jsonify({"error": "Car not found"}), 404
    return jsonify(car.to_dict(orient='records')[0])

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

@app.route("/")
def hello_world():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
