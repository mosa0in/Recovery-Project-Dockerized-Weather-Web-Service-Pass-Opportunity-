# Weather Web Service

A containerized Flask application that provides real-time weather information using the OpenWeatherMap API.

## Project Structure

```
.
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Example environment variables
└── README.md              # This file
```

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 1.29 or later)
- OpenWeatherMap API key (get one at https://openweathermap.org/api)

## Setup Instructions

### 1. Clone or Download the Project

```bash
cd weather-service
```

### 2. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env` and replace `your_api_key_here` with your OpenWeatherMap API key:

```
OPENWEATHER_API_KEY=your_actual_api_key
FLASK_ENV=production
FLASK_PORT=5000
API_PORT=5000
```

## Building and Running

### Option 1: Using Docker Compose (Recommended)

**Build and start the service:**

```bash
docker-compose up --build
```

The service will be available at `http://localhost:5000`

**Run in background:**

```bash
docker-compose up -d --build
```

**View logs:**

```bash
docker-compose logs -f weather-api
```

**Stop the service:**

```bash
docker-compose down
```

### Option 2: Using Docker Directly

**Build the image:**

```bash
docker build -t weather-api .
```

**Run the container:**

```bash
docker run -p 5000:5000 \
  -e OPENWEATHER_API_KEY=your_api_key \
  weather-api
```

### Option 3: Local Development (without Docker)

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Set environment variables:**

```bash
export OPENWEATHER_API_KEY=your_api_key
export FLASK_ENV=development
```

**Run the application:**

```bash
python app.py
```

## API Endpoints

### GET /weather

Retrieve weather information for a city.

**Query Parameters:**
- `city` (required, string): City name

**Example Request:**

```bash
curl "http://localhost:5000/weather?city=London"
```

**Success Response (200):**

```json
{
  "city": "London",
  "temperature": 15.2,
  "condition": "Cloudy",
  "timestamp": "2024-02-19T12:34:56.789123Z"
}
```

**Error Responses:**

- **400 Bad Request**: Missing city parameter or invalid city name
  ```json
  {"error": "Missing required parameter: city"}
  ```

- **404 Not Found**: City not found
  ```json
  {"error": "City not found: InvalidCity"}
  ```

- **429 Too Many Requests**: API rate limit exceeded
  ```json
  {"error": "Rate limit exceeded"}
  ```

- **500 Internal Server Error**: Service configuration error or API failure
  ```json
  {"error": "Service misconfiguration"}
  ```

- **503 Service Unavailable**: Cannot connect to OpenWeatherMap API
  ```json
  {"error": "Service unavailable"}
  ```

- **504 Gateway Timeout**: Request to OpenWeatherMap API timed out
  ```json
  {"error": "Request timeout"}
  ```

### GET /health

Health check endpoint.

**Example Request:**

```bash
curl http://localhost:5000/health
```

**Response (200):**

```json
{"status": "healthy"}
```

## Testing

### Manual Testing

**Test endpoint availability:**

```bash
curl http://localhost:5000/health
```

**Test weather endpoint with valid city:**

```bash
curl "http://localhost:5000/weather?city=Paris"
curl "http://localhost:5000/weather?city=New%20York"
curl "http://localhost:5000/weather?city=Tokyo"
```

**Test error handling:**

```bash
# Missing city parameter
curl "http://localhost:5000/weather"

# Invalid city
curl "http://localhost:5000/weather?city=InvalidCityXYZ123"

# Non-existent endpoint
curl http://localhost:5000/notfound
```

### Docker Health Check

The Docker container includes a built-in health check:

```bash
docker ps
```

The `HEALTHCHECK` will show as `healthy` when the service is running correctly.

### Automated Testing Script

Create `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"

echo "Testing health endpoint..."
curl -s "$BASE_URL/health" | python -m json.tool

echo -e "\n\nTesting weather endpoint..."
curl -s "$BASE_URL/weather?city=London" | python -m json.tool

echo -e "\n\nTesting error handling (missing parameter)..."
curl -s "$BASE_URL/weather" | python -m json.tool

echo -e "\n\nTesting error handling (invalid city)..."
curl -s "$BASE_URL/weather?city=InvalidCityXYZ" | python -m json.tool
```

Run the test script:

```bash
chmod +x test_api.sh
./test_api.sh
```

## Performance Considerations

- **Gunicorn**: The container runs 4 worker processes for concurrent request handling
- **Timeouts**: API requests timeout after 5 seconds
- **Caching**: Consider implementing Redis-based caching for repeated city queries
- **Rate Limiting**: Monitor OpenWeatherMap API usage to avoid rate limits

## Best Practices Implemented

### Docker Best Practices

- **Small base image**: Uses `python:3.11-slim` to reduce image size
- **Layer caching**: Optimized Dockerfile to maximize layer caching
- **No root user**: Application runs as non-root (inherited from base image)
- **Health checks**: Built-in health checks for orchestration systems
- **Environment variables**: Configuration via environment variables only
- **Multi-stage consideration**: Structured for future multi-stage optimization

### API Security

- **Input validation**: City names are validated for length and content
- **Error handling**: Comprehensive error handling with appropriate HTTP status codes
- **Timeout protection**: All external requests have timeouts
- **Logging**: Structured logging for monitoring and debugging
- **API key protection**: API key stored in environment variables only

### Code Quality

- **Error handling**: Specific exception handling for different failure modes
- **Logging**: Detailed logging for monitoring and troubleshooting
- **Code organization**: Clean separation of concerns
- **Documentation**: Comprehensive docstrings and comments

## Troubleshooting

### Container fails to start

**Check logs:**
```bash
docker-compose logs weather-api
```

**Common issues:**
- Invalid API key: Verify `OPENWEATHER_API_KEY` in `.env`
- Port already in use: Change `API_PORT` in `.env`

### API key errors

```
Invalid API credentials
```

- Verify your OpenWeatherMap API key is correct
- Check if the API key has expired or been revoked
- Ensure the API key is for the free/current plan

### Connection errors

```
Service unavailable
```

- Check internet connectivity
- Verify OpenWeatherMap API is accessible
- Check firewall/proxy rules

### Rate limiting

```
Rate limit exceeded
```

- Monitor API call frequency
- Implement caching for repeated queries
- Upgrade to a higher OpenWeatherMap plan

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | - | Yes |
| `FLASK_ENV` | Flask environment mode | `production` | No |
| `FLASK_PORT` | Flask port inside container | `5000` | No |
| `API_PORT` | External port mapping | `5000` | No |

## Maintenance

### Updating Dependencies

```bash
docker-compose up --build
```

### Monitoring

The application logs to stdout:

```bash
docker-compose logs -f weather-api
```

### Scaling

To handle more requests, increase the number of Gunicorn workers in the Dockerfile:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "30", "app:app"]
```

## License

MIT License
