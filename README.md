# NBS API

## Installation
`pip install nbsapi`

## Development
Ensure that you have [`uv`](https://docs.astral.sh/uv/) installed.

1. Clone the repo
2. Inside the repo, create a new virtual env, `.venv`, if you use Conda / Anaconda you can create a environment there and activate it. 
3. Activate it
4. Run `uv sync` to install packages
5. Run tests using `pytest .`
6. You can now run the FastAPI server using `uv run python src/nbsapi/main.py`
7. The API is available on `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`

## Updating the API
If you make changes to the API's public endpoints you must re-generate the API conformance verification tests:

1. run `uv run test_generator/test_generator.py --spec openapi.json` from the repo root, where `openapi.json` is the generated OpenAPI spec
2. Copy the generated Tavern YAML tests (located in `conformance/` by default) into the `nbsapi_verify` repo, to the path `src/nbsapi_verify/tests/`
3. Cut a new release of `nbsapi`, then tag and publish a new release of `nbs_verify` to PyPI (Github Actions will auto-publish when a new tag is pushed). The API and the conformance testing tool are now in sync.

## Database
We're using SQLAlchemy and [alembic](https://alembic.sqlalchemy.org/en/latest/). To run the reference app, you will need PostgreSQL data base with the PostGIS extension installed e.g on [Ubuntu](https://postgis.net/documentation/getting_started/install_ubuntu/). 

1. You'll need a Postgres database named `nbsapi`, with a user and password both set as `nbsapi`.
2. Ensure that the `.env` file reflects your database settings. A example [.env.sample](.env.sample) is provided
3. Ensure that PostGIS is installed _for your database_: in a SQL console: `CREATE EXTENSION postgis;`
4. Once that's set up, run `uv run alembic upgrade head` to migrate to the current state of the DB.

## SQL Commands for reference

SQL commands for creation of database and enabling the PostGIS are mentioned above are shown below: 

    ``` sql

    CREATE DATABASE nbsapi;
    ALTER DATABASE nbsapi SET search_path=public,postgis,contrib;
    \connect nbsapi;
    CREATE SCHEMA postgis;
    CREATE EXTENSION postgis SCHEMA postgis;
    CREATE USER nbsapi;
    ALTER ROLE nbsapi WITH PASSWORD 'nbsapi';   
    grant all privileges on database nbsapi to nbsapi;

    ```

To run a migration:

1. Make changes to models under `src/nbsapi/models/` (don't forget to import them in `src/nbsapi/models/__init__.py`)
2. Generate a revision using uv run alembic revision --autogenerate -m "description of change"
3. Inspect the generated revision in `src/alembic/versions`
4. When you're happy, apply it: `uv run alembic upgrade head` (you should also run this after you pull changes)
