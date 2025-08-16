#!/usr/bin/env python3
"""
WSGI file for Trading Journal Flask App
"""
import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

# Set Flask environment
os.environ['FLASK_ENV'] = 'production'

# Import the application
from journal import create_production_app

application = create_production_app()

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
