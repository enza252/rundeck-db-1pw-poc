up:
	docker-compose up

build: 
	docker-compose up --build

down: 
	docker-compose down


install:
	cd scripts && poetry install

requirements:
	cd scripts && poetry export -f requirements.txt > requirements.txt
