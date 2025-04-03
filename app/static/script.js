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
if (window.location.pathname.includes("specs")) {
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
							${car["Company Names"]} ${car["Cars Names"]}
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

function fetchCarDetails(carId) {
	fetch(`${API_BASE}/get_car/${carId}`)
		.then(response => {
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			return response.text();
		})
		.then(text => {
			// Clean response and parse JSON
			let cleanedText = text.replace(/NaN/g, "null");
			const car = JSON.parse(cleanedText);
			renderCarDetails(car);
		})
		.catch(error => {
			console.error("Error fetching car details:", error);
			showError('Error loading specifications. Please try again later.');
		});
}

function renderCarDetails(car) {
	if (!car || Object.keys(car).length === 0) {
		throw new Error('No car data received');
	}

	// Set main car info
	document.getElementById('carTitle').textContent = `${car["Company Names"]} ${car["Cars Names"]}`;
	document.getElementById('carPrice').textContent = car["Cars Prices"] ? `${car["Cars Prices"]}` : 'Price on request';

	// Set basic info
	const basicInfo = document.getElementById('carBasicInfo');
	basicInfo.innerHTML = `<p class="flex items-center">
    <img src="../static/engine.svg" class="w-5 h-5 mr-1" alt="Engine Icon">
    ${car["Engine"] || 'N/A'}
  </p>
  <p class="flex items-center">
    <img src="../static/speed.svg" class="w-5 h-5 mr-1" alt="Speed Icon">0-100 km/h in ${car["Performance"] || 'N/A'}
  </p>`;

	// Set car image
	const carImage = document.getElementById('carImage');
	carImage.src = car["Image"] || '/static/default_car.png';
	carImage.alt = `${car["Company Names"]} ${car["Cars Names"]}`;

	// Populate specifications
	const detailsContainer = document.getElementById('carDetails');
	detailsContainer.innerHTML = ''; // Clear previous content
	const importantSpecs = ["Top Speed", "Horsepower", "Torque", "Fuel Type", "CC/Battery Capacity", "Seats"];

	importantSpecs.forEach(spec => {
		if (car[spec]) {
			detailsContainer.innerHTML += `
        <div class="bg-gray-50 p-4 rounded-lg">
          <h4 class="font-medium text-gray-500">${spec}</h4>
          <p class="text-lg font-semibold text-gray-900">${car[spec]}</p>
        </div>
      `;
		}
	});
}

function showError(message) {
	const container = document.getElementById('carDetails') || document.createElement('div');
	container.innerHTML = `
    <div class="col-span-2 bg-red-50 p-4 rounded-lg text-center">
      <p class="text-red-600 font-medium">${message}</p>
    </div>
  `;
	if (!container.parentNode) {
		document.querySelector('main').appendChild(container);
	}
}

// Navigation Functions
function goToCarList(type) {
	window.location.href = `view`;
}

function goToHome() {
	window.location.href = "index.html";
}