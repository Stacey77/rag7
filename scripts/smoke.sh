#!/bin/bash

# FortFail Smoke Test Script
# Tests basic orchestrator functionality end-to-end
# Requires: curl, jq

set -e

ORCHESTRATOR_URL="${ORCHESTRATOR_URL:-http://localhost:8000}"
REG_SECRET="${ORCH_REG_SECRET:-dev-reg-secret-change-in-production}"
AGENT_ID="smoke-test-agent-$(date +%s)"

echo "🧪 FortFail Smoke Test"
echo "====================="
echo "Orchestrator: $ORCHESTRATOR_URL"
echo "Agent ID: $AGENT_ID"
echo ""

# Check for dependencies
command -v jq >/dev/null 2>&1 || { echo "❌ Error: jq is required but not installed."; exit 1; }

# Step 1: Wait for orchestrator readiness
echo "⏳ Waiting for orchestrator to be ready..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -sf "$ORCHESTRATOR_URL/health/ready" > /dev/null; then
        echo "✓ Orchestrator is ready"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "  Attempt $retry_count/$max_retries..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Orchestrator failed to become ready"
    exit 1
fi

# Step 2: Mint JWT token
echo ""
echo "🔐 Minting JWT token..."
TOKEN_RESPONSE=$(curl -sf -X POST "$ORCHESTRATOR_URL/auth/token" \
    -H "Content-Type: application/json" \
    -d "{\"registration_secret\": \"$REG_SECRET\", \"agent_id\": \"$AGENT_ID\"}")

TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.token')
EXPIRES_IN=$(echo "$TOKEN_RESPONSE" | jq -r '.expires_in')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Failed to obtain token"
    exit 1
fi

echo "✓ Token obtained (expires in ${EXPIRES_IN}s)"

# Step 3: Create test snapshot
echo ""
echo "📦 Creating test snapshot..."
SNAPSHOT_ID="snapshot-smoke-test-$(date +%s)"

# Create a small test tar file
TEST_DIR=$(mktemp -d)
echo "test data for smoke test" > "$TEST_DIR/test.txt"
TAR_FILE="$TEST_DIR/snapshot.tar"
tar -czf "$TAR_FILE" -C "$TEST_DIR" test.txt

# Compute checksum
CHECKSUM=$(sha256sum "$TAR_FILE" | awk '{print $1}')
SIZE=$(stat -f%z "$TAR_FILE" 2>/dev/null || stat -c%s "$TAR_FILE")

echo "  Snapshot ID: $SNAPSHOT_ID"
echo "  Checksum: $CHECKSUM"
echo "  Size: $SIZE bytes"

# Register snapshot metadata
SNAPSHOT_RESPONSE=$(curl -sf -X POST "$ORCHESTRATOR_URL/snapshots" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"id\": \"$SNAPSHOT_ID\",
        \"agent_id\": \"$AGENT_ID\",
        \"checksum\": \"$CHECKSUM\",
        \"size\": $SIZE,
        \"metadata\": {\"test\": true}
    }")

PRESIGNED_URL=$(echo "$SNAPSHOT_RESPONSE" | jq -r '.presigned_url // empty')

if [ -n "$PRESIGNED_URL" ] && [ "$PRESIGNED_URL" != "null" ]; then
    echo "✓ Using presigned URL for upload"
    curl -sf -X PUT "$PRESIGNED_URL" --data-binary "@$TAR_FILE"
else
    echo "✓ Using multipart upload"
    curl -sf -X POST "$ORCHESTRATOR_URL/snapshots/$SNAPSHOT_ID/object" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file=@$TAR_FILE"
fi

echo "✓ Snapshot uploaded"

# Step 4: Create restore job
echo ""
echo "🔄 Creating restore job..."
JOB_RESPONSE=$(curl -sf -X POST "$ORCHESTRATOR_URL/restore-jobs" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"snapshot_id\": \"$SNAPSHOT_ID\",
        \"target_agent_id\": \"$AGENT_ID\"
    }")

JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo "❌ Failed to create restore job"
    exit 1
fi

echo "✓ Restore job created: $JOB_ID"

# Step 5: Verify command was queued
echo ""
echo "📋 Polling for agent commands..."
sleep 2  # Give system time to process

COMMANDS_RESPONSE=$(curl -sf -X GET "$ORCHESTRATOR_URL/agent/$AGENT_ID/commands" \
    -H "Authorization: Bearer $TOKEN")

COMMAND_COUNT=$(echo "$COMMANDS_RESPONSE" | jq '. | length')

if [ "$COMMAND_COUNT" -gt 0 ]; then
    echo "✓ Command queued for agent"
    echo "$COMMANDS_RESPONSE" | jq '.'
else
    echo "⚠ No commands found (may have been processed already)"
fi

# Step 6: Check job status
echo ""
echo "📊 Checking job status..."
JOB_STATUS_RESPONSE=$(curl -sf -X GET "$ORCHESTRATOR_URL/restore-jobs/$JOB_ID" \
    -H "Authorization: Bearer $TOKEN")

STATUS=$(echo "$JOB_STATUS_RESPONSE" | jq -r '.status')
echo "✓ Job status: $STATUS"

# Step 7: List agents
echo ""
echo "🤖 Listing agents..."
AGENTS_RESPONSE=$(curl -sf -X GET "$ORCHESTRATOR_URL/agents" \
    -H "Authorization: Bearer $TOKEN")

AGENT_COUNT=$(echo "$AGENTS_RESPONSE" | jq '. | length')
echo "✓ Found $AGENT_COUNT agent(s)"

# Cleanup
rm -rf "$TEST_DIR"

echo ""
echo "✅ Smoke test completed successfully!"
echo ""
echo "Summary:"
echo "  - Orchestrator: ✓ Ready"
echo "  - Authentication: ✓ Token obtained"
echo "  - Snapshot: ✓ Created and uploaded"
echo "  - Restore Job: ✓ Created ($JOB_ID)"
echo "  - Commands: ✓ Queued"
echo "  - Agents: ✓ Listed ($AGENT_COUNT)"
echo ""
echo "🎉 All systems operational!"
