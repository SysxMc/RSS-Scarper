#!/bin/bash

# Pipe input from another command (e.g., `some_command`)
command_output=$(some_command)

# Extract the URL using grep or regex
url=$(echo "$command_output" | grep -oP 'http[s]?://\S+')

# If a URL was found, print it
if [ -n "$url" ]; then
  echo "Found URL: $url"
else
  echo "No URL found."
fi
