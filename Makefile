start/local:
	uvicorn app.main:app --reload

start/compose:
	docker compose up -d

stop/compose:
	docker compose down