# aubergine-test
Compress image and store the compressed image url

* create a folder and go inside that folder
* pull the project from https://github.com/fahim-15/aubergine-test.git development

* create a virtual env and activate
* install the requirement.txt file present at project folder
* Open .env file, replace ****** with proper keys.
* run migrations
* start the django local server and celery worker
django server: python manage.py runserver
celery worker: celery -A compressed_image worker -l info

run a command, 'python manage.py collectsatic' if needed.
go to browser and open 'your url'/swagger/

1. register user
2. Then check your mail and verify it and log in with username
3. copy the jwt token and paste it in Authorize section in top right corner.
4. Add downloadable image url list
5. Get the compressed image urls

