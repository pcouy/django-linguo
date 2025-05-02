# django-linguo Example Project

This is a minimal working example of the django-linguo library for model translations.

## Features Demonstrated

- MultilingualModel for translatable model fields
- MultilingualManager for querying models
- Regular ModelForms working with the current language
- MultilingualModelForms for editing all languages simultaneously (in Admin)
- Language switching 

## Setup

1. Make sure django-linguo is installed:
   ```
   pip install -e ..
   ```

2. Install Django and other dependencies:
   ```
   pip install Django
   ```

3. Migrate the database:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Create a superuser to access the admin:
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage Instructions

- Visit http://127.0.0.1:8000/ to see the main site
- Change languages using the buttons in the top-right of the page
- Create products and observe how the translatable fields change when switching languages
- Visit http://127.0.0.1:8000/admin/ to use the admin interface
- In the admin, you can edit all language fields at once using the MultilingualModelForm

## How It Works

1. The Product model inherits from MultilingualModel
2. In the model's Meta class, we define which fields are translatable
3. Django-linguo creates database columns for each language (name_en, name_fr, etc.)
4. The translation framework transparently handles retrievals and updates

Look at the Product model in `myproject/myapp/models.py` to see how the translatable fields are defined.

## Project Structure

- `myproject/` - The main Django project
  - `myapp/` - Example app with Product model
  - `settings.py` - Project settings with language configuration
- `templates/` - HTML templates for the site
- `manage.py` - Django management script 