#!/bin/bash

# Function to handle early termination
terminate_instances() {
    echo "Terminating all instances..."
    pkill -P $$  # Terminate child processes
    exit 1
}

# Trap the Ctrl+C signal to call the terminate_instances function
trap terminate_instances INT

# Check for the number of arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number of instances>"
    exit 1
fi

# Ensure the argument is a positive integer
if ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Error: Please provide a valid positive integer."
    exit 1
fi

# Number of instances to run
instances="$1"

# Loop to start the instances
for ((i = 1; i <= $instances; i++)); do
    echo "Starting instance $i"
    python3 http-client.py --domain=34.86.19.204 --port=5000 --bucket=/ds561-ptrandev-hw02 --webdir=html --num_requests=1000 --index=10000 &
done

# Wait for all instances to finish
wait

echo "All instances have completed."
