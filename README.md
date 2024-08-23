# fastapi-load-test
FastAPI Load Test

## Purpose
Setting up a simple test to compare performance of async and sync endpoints under load to identify if the webserver is the bottleneck in a production application. Specifically, looking to validate blocking and observe P99 increases as requests per sec increases. 

Per https://fastapi.tiangolo.com/async/#path-operation-functions, FastAPI executes sync endpoints on an external threadpool, whereas async endpoints are ran on a single thread and awaited in the event loop.

## Local Setup
1. Install Python and Poetry
```sh
brew install python@3.11

# https://python-poetry.org/docs/
brew install pipx
pipx install poetry
```
2. Create virtual environment
```sh
python3.11 -m venv fastapi-load-test-env
source fastapi-load-test-env/bin/activate
poetry install --no-root
```

3. Add dependencies
```sh
poetry add <package>
```

4. Dump poetry.lock to requirements.txt
```sh
poetry export --without-hashes --format=requirements.txt > docker/requirements.txt
```

## Running Test
1. Start Docker Compose
    - `make start/compose`
    - API docs are viewable at `localhost:8000/docs`, and Grafana at `localhost:3000` (user/pass is admin/admin)

2. Create observabilty dashboard
    - Import the JSON model from `dashboard/fastapi.json`. This dashboard has request per second time-series, latency heatmaps, P99, etc.

3. Run simulation

## Useful Links
- Example of otel middleware: https://github.com/blueswen/fastapi-observability/tree/main
- Docker image with otel, prom, and grafana: https://grafana.com/blog/2024/03/13/an-opentelemetry-backend-in-a-docker-image-introducing-grafana/otel-lgtm/