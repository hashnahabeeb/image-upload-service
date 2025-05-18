#!/bin/bash

# Set the directory containing the tests
TEST_DIR="tests"
TEST_OUTPUT_DIR="test-result"

# Run the tests and measure coverage
coverage run --omit "tests/*" -m unittest discover -s "$TEST_DIR"

# Check the exit status of the tests
if [ $? -eq 0 ]; then
  echo "All tests passed successfully."
else
  echo "Some tests failed. Check the output above for details."
  exit 1
fi

# Generate a coverage report in the terminal
coverage report -m

# Generate an HTML coverage report
coverage html -d $TEST_OUTPUT_DIR/coverage
