#!/bin/bash

# Configurations
CONFIGS=("default" "1" "2" "3")

# Loop through each configuration and run the tests
for CONFIG in "${CONFIGS[@]}"; do
    echo "Running tests with config: $CONFIG"
    pytest --config="$CONFIG"
done