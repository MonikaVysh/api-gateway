@echo off
REM Run linting checks

echo Running flake8...
flake8 .

echo Running mypy type checking...
mypy .

echo Linting complete!
pause