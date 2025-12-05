#!/bin/bash
# Test script for RAG7 API authentication

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "=== RAG7 API Authentication Test ==="
echo "Base URL: $BASE_URL"
echo

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq .
echo

# Test login
echo "2. Testing login endpoint..."
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "ERROR: Failed to get token"
  exit 1
fi

echo "✓ Login successful"
echo "Token: ${TOKEN:0:50}..."
echo

# Test protected endpoint without token
echo "3. Testing protected endpoint WITHOUT token (should fail)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}')
echo "$RESPONSE" | jq .

if echo "$RESPONSE" | grep -q "Not authenticated"; then
  echo "✓ Correctly rejected unauthenticated request"
else
  echo "ERROR: Should have been rejected"
  exit 1
fi
echo

# Test protected endpoint with token
echo "4. Testing protected endpoint WITH token (should succeed)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, RAG7!"}')
echo "$RESPONSE" | jq .

if echo "$RESPONSE" | grep -q "user"; then
  echo "✓ Successfully authenticated request"
else
  echo "ERROR: Authentication failed"
  exit 1
fi
echo

# Test refresh token
echo "5. Testing token refresh..."
NEW_TOKEN=$(curl -s -X POST "$BASE_URL/auth/refresh" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.access_token')

if [ "$NEW_TOKEN" = "null" ] || [ -z "$NEW_TOKEN" ]; then
  echo "ERROR: Failed to refresh token"
  exit 1
fi

echo "✓ Token refresh successful"
echo "New token: ${NEW_TOKEN:0:50}..."
echo

# Test protected info endpoint
echo "6. Testing protected info endpoint..."
curl -s "$BASE_URL/protected/info" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo

echo "=== All tests passed! ==="
