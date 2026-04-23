#!/bin/bash

# ============================================================================
# Traffic Generation Lab (HTTP Request Simulation)
# ============================================================================
# Educational purpose only - use in isolated lab environments
# ============================================================================

# Target URL (Metasploitable / lab environment)
TARGET="http://192.168.188.132/mutillidae/"

# Number of requests (default: 100)
REQUESTS=${1:-100}

# Delay between requests in seconds (default: 0.05)
DELAY=${2:-0.05}

echo "===== HTTP TRAFFIC GENERATION LAB ====="
echo "Target      : $TARGET"
echo "Requests    : $REQUESTS"
echo "Delay       : $DELAY seconds"
echo "Starting simulation..."

# Send HTTP requests in loop
for i in $(seq 1 $REQUESTS); do
    curl -s "$TARGET" > /dev/null &

    echo -ne "[$i/$REQUESTS] request sent...\r"

    sleep $DELAY
done

echo -e "\nSimulation completed."