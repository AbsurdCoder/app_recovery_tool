python3 -m venv env

# Activate virtual environment
# On Windows
# env\Scripts\activate
# On Unix or MacOS
source env/bin/activate

# Install Django and other required packages
pip install django pyyaml kafka-python requests psycopg2-binary pymongo

# Create Django project
django-admin startproject recovery_tool

# Navigate to project directory
cd recovery_tool

# Create app
python manage.py startapp workflow_builder

# Return to the project root
cd ..