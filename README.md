## Redis Proxy

### Tools used
- Python3.8 as the programming language
- Flask as the proxy server

### Overview
This proxy was written as a flask application that connects to a redis service. To interact with the proxy you can make REST calls to the flask application which then checks the local LRU cache for the existing user, if it is not found or if it is past the expiry time the user is retrieved from the redis database itself.

The LRU is built based off of python's Ordered Dict class and as such has algorithmic complexity of the followiing:
 - Deletion is O(1)
 - Checking for key O(1)
 - Insertion/Move to end O(1)

### Running the project
The Makefile for this project has 3 commands
 - make build
 - make up
 - make test

Make build and up run docker-compose build and up respectively with make test running docker-compose up then the unit tests found in ./tests/test_proxy.py
The tests initializes the redis database with 6 different users (1 more than the max cache size) and runs 4 tests. Testing the redis backing itself, the get request for a user, if setting max cache size in ./configs/config.yml (which contains the rest of the configurations specified in the assignment) works, testing LRU eviction, and testing the expiry timing.

As make test is the first command expected to be ran it includes the command to make the docker network ```docker network create proxy-network```. On proceding runs of make test that command should be commented out. If the docker images are running you can use the below curl command to test the functionality of the proxy. (While the set command was not part of the assignment I added it for additonal testing purposes).

Sample curl command for testing:

```curl --header "Content-Type: application/json" --request GET http://localhost:5000/get/?key=1```

```curl --header "Content-Type: application/json" --request POST --data '{"key": "1", "user": "bob"}' http://localhost:5000/set```