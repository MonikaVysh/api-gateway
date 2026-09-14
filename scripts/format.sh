#!/bin/bash
# Format code with black and isort

echo "Formatting code with black..."
black .

echo "Sorting imports with isort..."
isort .

echo "Code formatting complete!"