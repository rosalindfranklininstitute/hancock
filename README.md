# Hancock - Microservice for Pre-Signed URLs
## Structure
Hancock is a Flask Rest-API that generates pre-signed URLs from an S3 bucket for a given key and bucket. It is designed 
safely retrieve data from our Ceph S3 store without the need for access keys to be generated for the users.

Users will not have access to Hancock, it will be purely triggered from our data catalogue system Scicat, through the Jobs
mechanism. This mechanism creates a job entry in the mongo database layer of Scicat, which in turn triggers a message on RabbitMQ.
The information on this Job is then used by Hancock to retrieve the Pre-signed URL.

It is very difficult to find a mechanism where Flask can listen for messages, but still serve the REST-API. Currently there 
is a worker function in place that acts as a middleman between Scicat and Hancock. This application listens for new messages 
and processes them sending a http request to Hancock. 

## Running the Application

The easiest way to start the application is to use docker-compose.
```
docker-compose -f docker-compose-dev.yaml up --build
```
You will need to set up a .env file with the following fields:
```
HANCOCK_REDIS_HOST
LDAP_HOST
LDAP_PORT
LDAP_USE_SSL
LDAP_BASE_DN
LDAP_USER_LOGIN_ATTR
LDAP_USER_OBJECT_FILTER
LDAP_BIND_USER_DN
LDAP_BIND_USER_PASSWORD
LDAP_USER_SEARCH_SCOPE
S3_ENDPOINT_URL
ACCESS_KEY
SECRET_ACCESS_KEY
```
For testing you can add the following fields to the .env
```
TEST_USERNAME
TEST_PASSWORD
S3_ENDPOINT_URL_DEV
ACCESS_KEY_DEV
SECRET_ACCESS_KEY_DEV
```