const API_BASE = "http://127.0.0.1:5000";

function fetchCar(id) {
	return fetch(`${API_BASE}/get_car/${id}`)
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			return response.text(); // Get raw response first
		})
		.then(text => {
			let cleanedText = text.replace(/NaN/g, "null"); // Replace "NaN" with null
			return JSON.parse(cleanedText); // Convert to JSON
		})
		.catch(error => {
			console.error("Error fetching car details:", error);
			throw error; // Return the error to the caller
		});
}

function getAllCars() {
	return fetch(`${API_BASE}/get_all_cars`)
		.then(response => response.json())
		.catch(error => console.error("Error fetching cars:", error));
}