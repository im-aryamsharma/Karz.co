const API_BASE = "http://127.0.0.1:5000";

// Extract URL parameters
const urlParams = new URLSearchParams(window.location.search);
const pageType = urlParams.get("type"); // 'explore' or 'specs'
let carId = urlParams.get("id");

if (carId !== null && carId !== undefined) {
	carId = carId.replace(/['"]+/g, ''); // Removes any accidental quotes
	carId = parseInt(carId, 10); // Converts to integer
}

console.log("Car ID Extracted:", carId);

if (!carId) {
	console.error("Error: Car ID is missing from URL!");
}

// Load cars for the car_list.html
if (window.location.pathname.includes("car_list.html")) {
	document.addEventListener("DOMContentLoaded", function() {
		document.getElementById("pageTitle").textContent =
			pageType === "specs" ? "Select a Car for Specifications" : "Explore Cars & Reviews";
		fetchCarList(pageType);
	});
}

// Load reviews for reviews.html
if (window.location.pathname.includes("reviews.html")) {
	document.addEventListener("DOMContentLoaded", function () {
		fetchCarReviews(carId);
	});
}

// Load car details if on specs.html
if (window.location.pathname.includes("specs.html")) {
	document.addEventListener("DOMContentLoaded", function () {
		fetchCarDetails(carId);
	});
}

document.addEventListener("DOMContentLoaded", function () {
	// Attach event listener to the Back to Home button
	const homeButton = document.getElementById("backToHome");
	if (homeButton) {
		homeButton.addEventListener("click", goToHome);
	}
});

document.addEventListener("DOMContentLoaded", function () {
	const homeButton = document.getElementById("backToHome");
	if (homeButton) {
		homeButton.onclick = function()
		{
			console.log("Back to Home button clicked"); // Debugging log
			window.location.href = "/"; // Navigate to home page
		};
	}
});

const reviewsContainer = document.getElementById("reviews");
if (reviewsContainer) {
	reviewsContainer.innerHTML = randomReviews;
} else {
	console.warn("Skipping reviews update: 'reviews' container not found on this page.");
}

// Fetch car list and display as clickable links
function fetchCarList(type) {
	fetch(`${API_BASE}/get_all_cars`)
		.then(response => response.json())
		.then(cars => {
			let carListHTML = "<ul>";
			cars.forEach(car => {
				carListHTML += `
					<li>
						<a href="${type === 'explore' ? 'reviews.html' : 'specs.html'}?id=${car.ID}&type=${type}">
							${car.Make} ${car.Model} (${car.Year})
						</a>
					</li>
				`;
			});
			carListHTML += "</ul>";
			document.getElementById("carList").innerHTML = carListHTML;
		})
		.catch(error => console.error("Error fetching cars:", error));
}

// Fetch car reviews and display
function fetchCarReviews(carId) {
	console.log("Fetching reviews for car ID:", carId); // Debugging log

	const reviewsContainer = document.getElementById("reviews");

	if (!reviewsContainer) {
		console.warn("Skipping reviews update: 'reviews' container not found on this page.");
		return;
	}

	// Define sample reviews
	const sampleReviews = [
		{ username: "JohnDoe", comment: "Great car! Reliable and smooth.", rating: 5 },
		{ username: "CarEnthusiast22", comment: "Decent but could be better on fuel.", rating: 3 },
		{ username: "JaneSmith", comment: "Absolutely love it!", rating: 5 },
		{ username: "AutoFan99", comment: "Engine is powerful but maintenance is costly.", rating: 4 },
		{ username: "DriverX", comment: "Not bad, but not great either.", rating: 3 }
	];

	// Ensure reviews are unique by shuffling the array
	let shuffledReviews = sampleReviews.sort(() => Math.random() - 0.5);
	let selectedReviews = shuffledReviews.slice(0, 3); // Pick first 3 unique reviews

	// Build the review content
	let uniqueReviews = "<h3>Reviews for Selected Car</h3>";
	selectedReviews.forEach(review => {
		uniqueReviews += `
			<div>
				<strong>${review.username}</strong> rated: ${review.rating}/5
				<p>${review.comment}</p>
				<hr>
			</div>
		`;
	});

	// Inject unique reviews into the page
	reviewsContainer.innerHTML = uniqueReviews;
}

// Fetch car details and display
function fetchCarDetails(carId) {
	const carDetailsContainer = document.getElementById("carDetails");
	if (!carDetailsContainer) {
		console.error("Error: 'carDetails' container not found!");
		return;
	}

	fetch(`${API_BASE}/get_car/${carId}`)
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			return response.text(); // Get raw response first
		})
		.then(text => {
			console.log("Raw API Response:", text); // Debugging log

			// Fix: Replace "NaN" with null to avoid JSON error
			let cleanedText = text.replace(/NaN/g, "null");

			return JSON.parse(cleanedText); // Convert to JSON
		})
		.then(car => {
			console.log("Parsed Car Data:", car); // Debugging log

			if (!car || Object.keys(car).length === 0) {
				document.getElementById("carDetails").innerHTML = "<p>No specifications available for this car.</p>";
				return;
			}

			document.getElementById("carTitle").textContent = `${car.Make} ${car.Model} (${car.Year})`;
			let carDetailsHTML = "<h3>Specifications:</h3>";

			Object.keys(car).forEach(key => {
				carDetailsHTML += `<p><strong>${key}:</strong> ${car[key]}</p>`;
			});

			document.getElementById("carDetails").innerHTML = carDetailsHTML;
		})
		.catch(error => {
			console.error("Error fetching car details:", error);
			document.getElementById("carDetails").innerHTML = "<p>Error loading specifications. Please try again later.</p>";
		});
}

// Navigation Functions
function goToCarList(type) {
	window.location.href = `car_list.html?type=${type}`;
}

function goToHome() {
	window.location.href = "index.html";
}