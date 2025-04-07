# Karz.co

A lightweight web-based forum built with Python (Flask) where users can register, log in, and write reviews about cars. The system also includes a car search feature to help users find models they're interested in and view the specifications of the vehicles. Users can also leave reviews and ratings on the vehicles once registered and logged in to their account.

---

## Features

-  User Registration & Login
-  Post reviews for car models
-  Search for cars by company name and model
-  Leave a rating out of five stars
-  View the specs of the vehicles
-  Simple, responsive web interface
---

### Server deployment
####1. Get the project itself
```bash
git clone https://github.com/im-aryamsharma/Karz.co.git Karz.co
```
#### 2. Install all the needed packages
```bash
pip3 install -r requirements.txt
```
#### 3. Navigate to server directory:
```bash
cd app/
```
#### 4. Start the server:
```bash
flask --app __init__.py run
```
OR
EXAMPLE
```bash
python3 __init__.py
```
