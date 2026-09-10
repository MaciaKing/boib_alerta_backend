alembic upgrade head

python -m app.database.init_database

python -m app.workers.boib_extractor