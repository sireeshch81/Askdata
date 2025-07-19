# Alembic Migration Instructions

## Initializing Alembic (one-time setup)

From the `dw-backend` directory, run:

```bash
alembic init migrations
```

## Generating the Initial Migration

After defining your SQLAlchemy models in `models.py`, generate the initial migration:

```bash
alembic revision --autogenerate -m "Initial migration"
```

## Generating New Migrations

Whenever you update your models, create a new migration:

```bash
alembic revision --autogenerate -m "Describe your change"
```

## Applying Migrations to the Database

To apply all migrations to your database:

```bash
alembic upgrade head
```

## Notes
- Ensure your `alembic.ini` and `env.py` are configured to point to the correct database and import your models.
- If you encounter missing tables in migrations, check that all models are imported in `env.py`.

