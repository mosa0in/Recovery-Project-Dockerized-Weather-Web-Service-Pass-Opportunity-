import requests
import json
import sys
from typing import Dict, Any, Tuple

BASE_URL = "http://localhost:5000"
TIMEOUT = 5

class WeatherAPITester:
    def __init__(self, base_url: str = BASE_URL, timeout: int = TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_total = 0

    def print_test_header(self, test_name: str, description: str):
        print(f"\n{'=' * 60}")
        print(f"TEST: {test_name}")
        print(f"Description: {description}")
        print(f"{'=' * 60}")

    def print_result(self, passed: bool, expected_status: int, actual_status: int, response: Dict[str, Any]):
        self.tests_total += 1
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"\nStatus: {status}")
        print(f"Expected: {expected_status}, Got: {actual_status}")
        print(f"Response: {json.dumps(response, indent=2)}")

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_health_check(self):
        self.print_test_header("Health Check", "Verify service is running")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            data = response.json()
            passed = response.status_code == 200 and data.get("status") == "healthy"
            self.print_result(passed, 200, response.status_code, data)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.tests_failed += 1
            self.tests_total += 1

    def test_valid_city(self, city: str):
        self.print_test_header(f"Valid City - {city}", f"Retrieve weather for {city}")
        try:
            response = requests.get(f"{self.base_url}/weather?city={city}", timeout=self.timeout)
            data = response.json()

            passed = (
                response.status_code == 200 and
                "city" in data and
                "temperature" in data and
                "condition" in data and
                "timestamp" in data
            )
            self.print_result(passed, 200, response.status_code, data)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.tests_failed += 1
            self.tests_total += 1

    def test_missing_parameter(self):
        self.print_test_header("Missing Parameter", "Error when city parameter is missing")
        try:
            response = requests.get(f"{self.base_url}/weather", timeout=self.timeout)
            data = response.json()
            passed = response.status_code == 400 and "error" in data
            self.print_result(passed, 400, response.status_code, data)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.tests_failed += 1
            self.tests_total += 1

    def test_invalid_city(self):
        self.print_test_header("Invalid City", "Error when city does not exist")
        try:
            response = requests.get(
                f"{self.base_url}/weather?city=InvalidCityXYZ12345",
                timeout=self.timeout
            )
            data = response.json()
            passed = response.status_code == 404 and "error" in data
            self.print_result(passed, 404, response.status_code, data)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.tests_failed += 1
            self.tests_total += 1

    def test_empty_city(self):
        self.print_test_header("Empty City Parameter", "Error when city parameter is empty")
        try:
            response = requests.get(f"{self.base_url}/weather?city=", timeout=self.timeout)
            data = response.json()
            passed = response.status_code == 400 and "error" in data
            self.print_result(passed, 400, response.status_code, data)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.tests_failed += 1
            self.tests_total += 1

    def test_nonexistent_endpoint(self):
        self.print_test_header("Non-existent Endpoint", "Error for undefined endpoint")
        try:
            response = requests.get(f"{self.base_url}/nonexistent", timeout=self.timeout)
            data = response.json()
            passed = response.status_code == 404 and "error" in data
            self.print_result(passed, 404, response.status_code, data)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.tests_failed += 1
            self.tests_total += 1

    def print_summary(self):
        print(f"\n{'=' * 60}")
        print("TEST SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total Tests: {self.tests_total}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"{'=' * 60}\n")

        if self.tests_failed == 0:
            print("✓ All tests passed!")
            return 0
        else:
            print("✗ Some tests failed!")
            return 1

    def run_all_tests(self):
        print("Starting Weather API Test Suite...\n")
        print(f"Base URL: {self.base_url}")
        print(f"Timeout: {self.timeout}s\n")

        self.test_health_check()
        self.test_valid_city("London")
        self.test_valid_city("Paris")
        self.test_valid_city("New York")
        self.test_missing_parameter()
        self.test_invalid_city()
        self.test_empty_city()
        self.test_nonexistent_endpoint()

        return self.print_summary()

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    tester = WeatherAPITester(base_url=base_url)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
