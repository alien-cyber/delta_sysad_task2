#!/bin/sh

# Run the initialization script
python3 init.py mentee.txt mentor.txt

# Start the Gunicorn server
exec gunicorn 'app:app' --bind=0.0.0.0:8000
