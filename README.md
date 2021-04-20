# Hancock - Microservice for Pre-Signed URLs
## Structure
Hancock is a Flask Rest-API that generates pre-signed URLs from an S3 bucket for a given key and bucket. It is designed 
safely retrieve data from S3 without need for access keys to be generated for the users. 

Users will not have access to Hancock, it will be purely triggered from other systems, such as a data cataloguing system.This system would  trigger a message on RabbitMQ. The information in this message is then used by Hancock to retrieve the Pre-signed URL.

It is very difficult to find a mechanism where Flask can listen for messages, but still serve the REST-API. Currently there 
is a worker function in place that acts as a middleman between Scicat and Hancock. This application listens for new messages 
and processes them sending a http request to Hancock. You can find this at the xchanger repo.

## Running the Application

The easiest way to start the application is to use docker-compose.
```
docker-compose -f docker-compose-dev.yaml up --build
```
You will need to set up a .env file with the following fields:
```
USER_SETUP_JSON
S3_ENDPOINT_URL
ACCESS_KEY
SECRET_ACCESS_KEY
TEST_S3_ENDPOINT_URL
HANCOCK_REDIS_HOST
SCICAT_URL
```
The User set up json will contain the user name and password of the service, or few services that you want to work with hancock.
Structure should look like:
```
{"myservice1":"servicepassword",
"myservice2":"servicespassword2"}
```
Please remember to set up a redis services in docker before running the app!