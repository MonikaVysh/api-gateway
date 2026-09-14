@echo off
REM Run tests

echo Running tests...
python test_auth.py
python test_rate_simple.py

echo Tests complete!
pause