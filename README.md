## Task CRUD API

A CRUD API for managing a to-do list, built with Python + FastAPI, running in Docker with a real PostgreSQL database. The app and database start together with a single command: docker compose up.

This builds directly on A2 (SQLite): the API, routes, validation, status codes, error format has not changed at all. Only the storage layer underneath it was swapped, from SQLite to a Postgres repository, proving that "switch storage" really does mean changing one file, not rewriting the app.


## Architecture

• `main.py` — FastAPI routes, request validation, error handling. **No SQL lives here.**

• `repository.py` — the only file that talks to the database (Postgres, via `psycopg2`). Every function takes and returns plain Python values, so `main.py` has no idea what database is behind it.

• `db.py` — opens a Postgres connection using `DATABASE_URL` from the environment.

• `init.sql` — creates the `tasks` table and seeds 3 example rows. Runs automatically the first time the Postgres container starts with an empty volume.

• `Dockerfile` — builds the FastAPI app into a container image.

• `docker-compose.yml` — starts the `app` and `db` containers together, networked so the app can reach Postgres by service name.



# How to run it
bash
cp .env.example .env
docker compose up

# Then open:

http://localhost:8000 — API info
http://localhost:8000/docs — Swagger UI

This single command starts both containers: db (Postgres, with a named volume so data persists) and app (this API). The app waits for Postgres to report healthy before it starts.

To stop everything: docker compose down. This removes the containers but not the volume — your data survives. Only docker compose down -v wipes the volume too.

# Environment variables

The connection string lives in .env, which is gitignored and never committed, it's the kind of file that can end up holding real credentials. A committed .env.example documents what's needed instead:

DATABASE_URL=postgresql://taskuser:taskpass@db:5432/taskdb

Inside Docker Compose, the app reaches Postgres via the service name db, Compose creates an internal network where db resolves to the Postgres container. This is different from running things locally, where you'd use localhost.

## Database setup

Postgres runs in Docker with a named volume (pgdata) mounted at /var/lib/postgresql/data. This is what makes data outlive the container itself, removing or rebuilding the db container doesn't touch the volume.

The tasks table is created by init.sql, mounted into Postgres's docker-entrypoint-initdb.d/ folder. The official Postgres image only runs scripts in that folder once, the very first time the container starts with an empty volume, which is also what guarantees the 3 example tasks are seeded exactly once, never duplicated on later restarts.

## Endpoints

| Method | Path        | Description                 | Success | Errors                           |
| ------ | ----------- | --------------------------- | ------- | -------------------------------- |
| GET    | /           | API info                    | 200     | —                                |
| GET    | /health     | Health check                | 200     | —                                |
| GET    | /tasks      | List all tasks              | 200     | —                                |
| GET    | /tasks/{id} | Get one task                | 200     | 404 unknown id                   |
| POST   | /tasks      | Create a task               | 201     | 400 missing/empty title          |
| PUT    | /tasks/{id} | Replace a task's title/done | 200     | 400 invalid body, 404 unknown id |
| DELETE | /tasks/{id} | Delete a task               | 204     | 404 unknown id                   |


# What changed vs. what didn't (the actual point of this assignment)

# Changed:

repository.py — rewritten from SQLite (sqlite3) to Postgres (psycopg2)
db.py — new file, opens a Postgres connection instead of a SQLite file
init.sql — new, Postgres-flavored table creation + seed script
requirements.txt — added psycopg2-binary, python-dotenv
New: Dockerfile, docker-compose.yml, .env, .env.example

# Did not change, at all:

main.py — every route, every status code, both exception handlers
The TaskCreate / TaskUpdate Pydantic models and validation rules
The {"error": "..."} error response shape
The API's external behavior, a client sending requests can't tell the difference

## Persistence proof

How I checked, exactly:

1. docker compose up - stack starts, 3 example tasks visible at GET /tasks
2. Created a new task: POST /tasks with {"title": "Learn Docker"} → returned 201 with id: 4
3. docker compose down — stops and removes both containers
4. docker compose up — stack starts fresh from the existing volume
5. GET /tasks — all 4 tasks still present, including "Learn Docker"

This confirms persistence across a full app + container restart, not just an app-level restart like the SQLite version proved. The data survives because it lives in the named volume pgdata, which exists independently of the containers, deleting and recreating the containers never touches it.