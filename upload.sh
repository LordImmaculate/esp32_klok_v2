#!/bin/bash

# Check if a port was provided
if [ -z "$1" ]; then
    echo "Error: Please provide the serial port as an argument."
    echo "Usage: ./upload.sh /dev/ttyUSB0"
    exit 1
fi

# Configuration
PORT="$1"
LOCAL_DIR="./src"    # Local directory with your MicroPython code
REMOTE_DIR="/pyboard" # Target directory on the MicroPython board

echo "Connecting to $PORT for file synchronization..."
echo "--- rshell rsync output ---"

# 1. Use rsync to copy only changed files and print the output
# The 'rshell' command will execute 'rsync' and its output will be printed directly
rshell -p $PORT rsync $LOCAL_DIR/ $REMOTE_DIR/

# Check the exit status of the rsync command
if [ $? -ne 0 ]; then
    echo "--- rsync failed! Aborting soft reset. ---"
    exit 1
fi

echo "--- rshell soft reset output ---"

# 2. Soft reset the board to run the new code immediately and print the output
# The 'repl' command allows sending commands to the MicroPython REPL
rshell -p $PORT repl "~ import machine ~ machine.soft_reset() ~"

echo "-----------------------------------"
echo "✅ Synchronization and soft reset complete for port $PORT."