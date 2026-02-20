import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
REQUEST_TIMEOUT = 5

# Validation
if not OPENWEATHER_API_KEY:
    logger.warning('OPENWEATHER_API_KEY environment variable not set')


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Get weather information for a city.

    Query Parameters:
        city (str): City name

    Returns:
        JSON: {
            'city': str,
            'temperature': float,
            'condition': str,
            'timestamp': str
        }
    """
    try:
        city = request.args.get('city')

        # Validation
        if not city:
            return jsonify({'error': 'Missing required parameter: city'}), 400

        if not OPENWEATHER_API_KEY:
            logger.error('API key not configured')
            return jsonify({'error': 'Service misconfiguration'}), 500

        city = city.strip()
        if not city or len(city) > 100:
            return jsonify({'error': 'Invalid city name'}), 400

        # API request
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }

        try:
            response = requests.get(
                OPENWEATHER_BASE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
        except requests.exceptions.Timeout:
            logger.error(f'Timeout fetching weather for {city}')
            return jsonify({'error': 'Request timeout'}), 504
        except requests.exceptions.ConnectionError:
            logger.error('Connection error to OpenWeatherMap API')
            return jsonify({'error': 'Service unavailable'}), 503
        except requests.exceptions.RequestException as e:
            logger.error(f'Request error: {str(e)}')
            return jsonify({'error': 'Failed to fetch weather data'}), 500

        # Handle API error responses
        if response.status_code == 401:
            logger.error('Invalid API key')
            return jsonify({'error': 'Invalid API credentials'}), 500
        elif response.status_code == 404:
            logger.info(f'City not found: {city}')
            return jsonify({'error': f'City not found: {city}'}), 404
        elif response.status_code == 429:
            logger.warning('API rate limit exceeded')
            return jsonify({'error': 'Rate limit exceeded'}), 429
        elif response.status_code != 200:
            logger.error(f'API error: {response.status_code}')
            return jsonify({'error': 'Failed to fetch weather data'}), 500

        # Parse response
        try:
            data = response.json()
        except ValueError:
            logger.error('Invalid JSON response from API')
            return jsonify({'error': 'Invalid API response'}), 500

        # Extract weather information
        try:
            city_name = data.get('name', 'Unknown')
            temperature = data['main']['temp']
            condition = data['weather'][0]['main']
            timestamp = datetime.utcnow().isoformat() + 'Z'

            result = {
                'city': city_name,
                'temperature': temperature,
                'condition': condition,
                'timestamp': timestamp
            }

            logger.info(f'Successfully fetched weather for {city_name}')
            return jsonify(result), 200

        except (KeyError, IndexError) as e:
            logger.error(f'Missing data in API response: {str(e)}')
            return jsonify({'error': 'Invalid API response structure'}), 500

    except Exception as e:
        logger.error(f'Unexpected error in get_weather: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f'Internal server error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
