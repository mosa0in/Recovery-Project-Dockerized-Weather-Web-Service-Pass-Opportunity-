#!/bin/bash

set -e

BASE_URL="${1:-http://localhost:5000}"
TIMEOUT="${2:-5}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_count=0
pass_count=0
fail_count=0

run_test() {
    local test_name=$1
    local url=$2
    local expected_status=$3
    local description=$4

    test_count=$((test_count + 1))
    echo -e "${YELLOW}Test $test_count: $test_name${NC}"
    echo "  Description: $description"
    echo "  URL: $url"
    echo "  Expected Status: $expected_status"

    response=$(curl -s -w "\n%{http_code}" --connect-timeout "$TIMEOUT" "$url" 2>&1 || echo "CONNECTION_ERROR\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    echo "  Response Status: $http_code"
    echo "  Response Body:"
    echo "$body" | python -m json.tool 2>/dev/null || echo "$body"

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "  ${GREEN}✓ PASSED${NC}\n"
        pass_count=$((pass_count + 1))
    else
        echo -e "  ${RED}✗ FAILED${NC}\n"
        fail_count=$((fail_count + 1))
    fi
}

echo -e "${YELLOW}=== Weather API Test Suite ===${NC}\n"
echo "Base URL: $BASE_URL"
echo -e "Timeout: ${TIMEOUT}s\n"

# Health check
run_test \
    "Health Check" \
    "$BASE_URL/health" \
    "200" \
    "Check if service is running"

# Valid city - London
run_test \
    "Valid City - London" \
    "$BASE_URL/weather?city=London" \
    "200" \
    "Retrieve weather for London"

# Valid city - Paris
run_test \
    "Valid City - Paris" \
    "$BASE_URL/weather?city=Paris" \
    "200" \
    "Retrieve weather for Paris"

# Valid city with spaces
run_test \
    "Valid City with Spaces - New York" \
    "$BASE_URL/weather?city=New%20York" \
    "200" \
    "Retrieve weather for New York (URL encoded)"

# Missing parameter
run_test \
    "Missing City Parameter" \
    "$BASE_URL/weather" \
    "400" \
    "Error when city parameter is not provided"

# Invalid city
run_test \
    "Invalid City" \
    "$BASE_URL/weather?city=InvalidCityXYZ12345" \
    "404" \
    "Error when city does not exist"

# Empty city parameter
run_test \
    "Empty City Parameter" \
    "$BASE_URL/weather?city=" \
    "400" \
    "Error when city parameter is empty"

# Non-existent endpoint
run_test \
    "Non-existent Endpoint" \
    "$BASE_URL/nonexistent" \
    "404" \
    "Error for undefined endpoint"

# Invalid method
run_test \
    "Invalid HTTP Method" \
    "$BASE_URL/weather" \
    "405" \
    "Error when using POST instead of GET" \
    || true

echo -e "${YELLOW}=== Test Summary ===${NC}"
echo -e "Total Tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"

if [ $fail_count -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi
