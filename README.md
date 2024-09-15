**Flight Price Finder API**
    This is a Django REST API that provides the cheapest flight prices based on the origin, destination, and travel date. The application caches API responses using Redis to optimize performance and minimize API calls. The project is containerized using Docker for easy setup and deployment.

**Table of Contents**
    - Features
    - APIs
        -> Ping API
        -> Get Cheapest Flight Price API
    - Running with Docker
    - Caching and Token Management
    - Assumptions

**Features**
    - Fetches cheapest flight prices from an external API.
    - Caches API responses for faster performance using Redis.
    - Uses token-based authentication to communicate with external flight data providers.
    - Containerized with Docker for easy deployment and development.

**APIs**
    Ping API:
        This is a simple API to check if the server is active.

        URL: /ping/
        Method: GET
        Response:
            {
                "data": "pong"
            }

    Get Cheapest Flight Price API:
        Fetches the cheapest flight offer based on the origin, destination, and travel date.

        URL: /flights/price?origin={origin_code}&destination={destination_code}&date={yyyy-mm-dd}&nocache={1}
        Method: GET
        Parameters:
            origin: IATA code of the origin airport.
            destination: IATA code of the destination airport.
            date: Departure date in yyyy-mm-dd format.
            nocache: (Optional) If set to true, fetches fresh data without using the cache.
        Response:
            {
                "data": {
                    "origin": "PAR",
                    "destination": "LAD",
                    "departure_date": "2024-09-27",
                    "price": "477.65 EUR"
                }
            }

**Running with Docker**

    1. Build and Run Containers
        Make sure Docker is installed on your system, then use the following commands:
            -> docker-compose up --build

        This will start up two services:
            django: The Django app running on port 8000.
            redis: The Redis service for caching.

    2. Access the Application
        Once the containers are up, you can access the APIs:
            Django App: http://localhost:8000/
            Ping API: http://localhost:8000/ping/
            Flight Price API: http://localhost:8000/flights/price?origin=JFK&destination=LAX&date=2024-12-01

**Caching and Token Management**

    Token Management:
        The API uses token-based authentication with a token that expires every 30 minutes. Instead of fetching a new token on every request, the application caches the token using Redis. When a token is requested:
            - If a valid token is available in the cache, it is reused.
            - If the token has expired or is not present in the cache, a new token is fetched from the external API and stored in Redis for 30 minutes.
        This process ensures that no manual token refresh is required during testing or production usage.

    Response Caching:
        Flight data responses are also cached in Redis. When a flight price is requested:
            - If a cached response is available for the origin, destination, and travel date, it is returned (unless the nocache query parameter is set to true).
            - If no cache is available, a fresh request is made to the external API, and the response is cached for 10 minutes.

**Assumptions**

    - Access Tokens: The application assumes that the access token's expiry time is strictly 30 minutes, and Redis handles the token's expiration automatically.
    - Redis for Caching: Redis is used for both token and flight data caching. Ensure Redis is properly configured and accessible within the Docker network.
    - External API Availability: The external flight API (e.g., Amadeus) is assumed to be consistently available during testing.