
# Create a virtual environment
python -m venv env

# Activate virtual environment
source env/bin/activate  # On Windows use: env\Scripts\activate


# Create necessary directories for templates
mkdir -p recovery_tool/workflow_builder/migrations

# Initialize the Django project and app
cd recovery_tool
django-admin startproject recovery_tool .
python manage.py startapp workflow_builder

# Now we'll create all the necessary files
# We'll do this in subsequent steps

# After creating files, run migrations
python manage.py makemigrations
python manage.py migrate

# Run the server
python manage.py runserver
