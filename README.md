# API-Project
Flight delay compensation and automated claim processing
Flight Delay Compensation API
Overview
The Flight Delay Compensation API is a Flask-based web application designed to manage flight delay compensation claims. It allows passengers to submit claims for flight delays, check the status of their claims, and view compensation rules. Additionally, it provides administrative functionalities for managing flights and claims.

Features
Submit Claims: Passengers can submit claims for flight delays.

Check Claim Status: Passengers can check the status of their claims using either the claim ID or their name and flight number.

Compensation Rules: View the rules for flight delay compensation based on the duration of the delay.

Admin Panel: Admins can manage flights, view all claims, and calculate compensation for claims.

Authentication: Secure JWT-based authentication for admin endpoints.

Installation
Clone the Repository:

bash
Copy
git clone https://github.com/Aminemaaloul/flight-delay-compensation-api.git
cd flight-delay-compensation-api
Set Up Environment Variables:
Create a .env file in the root directory and add the following variables:

plaintext
Copy
AVIATIONSTACK_API_KEY=your_api_key
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
FLASK_APP=app
FLASK_ENV=development
FLASK_DEBUG=1
Install Dependencies:

bash
Copy
pip install -r requirements.txt
Initialize the Database:

bash
Copy
python create_admin.py
Run the Application:

bash
Copy
python run.py
API Endpoints
Claims
Submit a Claim:

POST /api/claims

Submit a new claim for flight delay compensation.

Check Claim Status:

GET /api/claims/status

Retrieve the status of a claim using either the claim ID or the passenger name and flight number.

Get Compensation Rules:

GET /compensation-rules

View the rules for flight delay compensation based on the duration.

Admin
Get All Claims:

GET /admin/claims

Get a list of all claims (Admin Only).

Calculate Claim Compensation:

GET /admin/claims/compensation/<int:claim_id>

Calculate eligible compensation for a claim and update its status (Admin Only).

Get Claim Details:

GET /admin/claims/<int:claim_id>

Get detailed information about a specific claim by ID (Admin Only).

Flights
Get All Flights:

GET /api/flights

Fetch all flights departing from Tunis-Carthage Airport (TUN).

Add a Flight:

POST /admin/flights

Add a new flight to the database (Admin Only).

Get Flight Details:

GET /api/flights/<string:flight_number>

Fetch the details of a specific flight by its flight number.

Update Flight Details:

PUT /admin/flights/<string:flight_number>

Update details of a specific flight by flight number (Admin Only).

Delete a Flight:

DELETE /admin/flights/<string:flight_number>

Delete a specific flight by flight number (Admin Only).

Authentication
Login:

POST /admin/login

Authenticate and receive a JWT token for accessing protected endpoints.

Database Models
Admin: Stores admin user information.

Flight: Stores flight details including departure and arrival information.

Claim: Stores claim details including passenger name, flight number, and claim status.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Flask

SQLAlchemy

Marshmallow

JWT
