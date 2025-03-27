Fungalmaterials
===

### Description
A curated list on fungal material references.


### Contributing
If you want to contribute, you can open a pull request or if you don't have any code, open an issue for suggestions.


### Local development

To use this locally, you can use SQLite, so you don't need a full RDBMS install.
Running this requires python and a venv is recommended. It would work something like this:

1. Create and activate the virtual environment if you don't have one yet, this is set to not be included in git via `.gitignore`:
````shell
# From inside this repository after cloning it:
python -m venv venv
````

This will create a virtual environment named `venv` and you can activate it as follows:

````shell
source ./venv/bin/activate
````

At this point, all pip actions and dependencies will be constrained to this directory and not affect your OS.

2. Install any dependencies:

````shell
# From the activated virtual environment:
pip install -r requirements.txt
````

Note: some operating systems and package managers might rename python and pip to versioned ones like `python3` and `pip3`. 
Sometimes pip has to be used as a python3 module, instead of using `pip` you would use `python -m pip`.

3. Make a local environment setup

The current configuration automatically uses an insecure token and local SQLite DB for development purposes.
To override this you have to create a dotenv file, (aptly named `.env`) with contents suitable for your setup. An example is provided in `env-example`.

For local SQLite development you might want to replace the .env examples with:

````
DB_ENGINE = 'django.db.backends.sqlite3'
DB_NAME = 'db.sqlite3'
DB_USER = 'sqlite'
DB_HOST = 'localhost'
DB_PASSWORD = 'sqlite'
````

4. Once your environment is setup, you can start the django development server and optionally run migrations:

````shell
# Run migrations if needed, this makes sure your database is provisioned
python manage.py migrate
# Run the development server
python manage.py runserver
````

5. Populate with data (recommended order)
   
````shell
# Populate the Methods
python3 manage.py populate_methods
# Populate the Topics
python3 manage.py populate_topics
# Populate the Species
python3 manage.py populate_species
# Populate with Articles
python3 manage.py populate_articles
# Populate with Reviews
python3 manage.py populate_reviews
````

Other activities like creating new migrations or adding/upgrading packages are left as an exercise to the reader.
