# aubergine-test

## Compress image and store the compressed image url

### Task 1a:
User Registration
On Registration send an email to the User 
The email body should have verification link
### Task 1b:
Setup Celery
Setup RabbitMQ
### Task 1c:
After User Login (with credentials in Task 1a)
Add Multiple Image URLs
These Image URLs can be from any web storage like the S3 bucket.

On submitting of all these Image URLs store this URL's in the database in 2 ways:
* Original URL of the Image
* Compressed URL of the Image

##### Note: Consider Django Rest for API development and Postgres as Database for the above requirements.
