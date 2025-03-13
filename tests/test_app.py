# Import sys module for modifying Python's runtime environment
import sys

# Import os module for interacting with the operating system
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app instance from the main app file
from app import app 

# Import pytest for writing and running tests
import pytest

@pytest.fixture
def client():
	"""A test client for the app."""
	with app.test_client() as client:
		yield client

def test_home(client):
	"""Test the home route"""
	response = client.get('/')
	assert response.status_code == 200

def test_reviews(client):
	"""Test reviews route"""
	response = client.get('/reviews.html')
	assert response.status_code == 200

def test_car_list(client):
	"""Test car_list route"""
	response = client.get('/car_list.html')
	assert response.status_code == 200

def test_specs(client):
	"""Test specs route"""
	response = client.get('/specs.html')
	assert response.status_code == 200

def test_get_all_cars(client):
	"""Test to get all cars"""
	response = client.get('/get_all_cars')
	assert response.status_code == 200

def test_get_specific_car(client):
	"""Test for getting specs on specific car"""
	response = client.get(f"/get_car/10")
	assert response.status_code == 200

def test_get_review(client):
	"""Test for getting reviews"""
	response = client.get("/get_reviews/10")
	assert response.status_code == 200

def test_non_existent_route(client):
	"""Test for a non-existent route"""
	response = client.get('/non-existent')
	assert response.status_code == 404