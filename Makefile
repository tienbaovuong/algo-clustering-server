dev:
	docker-compose up -d

dev-down:
	docker-compose down

start:
	uvicorn main:app --host 0.0.0.0 --port 80

start-reload:
	python main-hotload.py

handler: app/worker
	celery -A app.worker.celery worker -l INFO -O fair -Q celery,nlp,clustering