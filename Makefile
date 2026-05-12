.PHONY: build up down logs seed test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

seed:
	docker-compose exec backend python services/log_generator.py --count 5000

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	rm -rf data/*.db
	rm -rf dataset/*.log dataset/*.csv dataset/*.json
