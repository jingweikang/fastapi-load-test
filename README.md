# fastapi-load-test
FastAPI Load Test

## Purpose
Setting up a simple test to compare performance of async and sync endpoints under load to identify if the webserver is the bottleneck in a production application. Specifically, looking to validate blocking and observe P99 increases as requests per sec increases. 

Per https://fastapi.tiangolo.com/async/#path-operation-functions, FastAPI executes sync endpoints on an external threadpool, whereas async endpoints are ran on a single thread and awaited in the event loop.

## Local Setup
### Install Python and Poetry
```sh
brew install python@3.11

# https://python-poetry.org/docs/
brew install pipx
pipx install poetry
```
### Create Virtual Environment
```sh
python3.11 -m venv fastapi-load-test-env
source fastapi-load-test-env/bin/activate
poetry install --no-root
```

### Add Dependencies
```sh
poetry add <package>
```

### Dump poetry.lock to requirements.txt
```sh
poetry export --without-hashes --format=requirements.txt > docker/requirements.txt
```

## Running Test 
