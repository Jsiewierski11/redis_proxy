build:
	docker network create proxy-network
	docker-compose build
up:
	docker-compose up
test:
	docker network create proxy-network
	docker-compose up -d
	docker exec flask-proxy python -m unittest discover -p "test_proxy.py" -v