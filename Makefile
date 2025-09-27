.PHONY: test test-local test-docker test-ci

test-local:
	cd app && pytest -v --tb=short tests/

test-docker:
	docker-compose -f docker-compose.test.yml up --build --exit-code-from tests

test-ci:
	docker-compose -f docker-compose.test.yml up --build --exit-code-from tests && docker-compose -f docker-compose.test.yml down

test: test-docker

test-auth:
	docker-compose -f docker-compose.test.yml run tests pytest -v app/tests/test_auth.py

test-tasks:
	docker-compose -f docker-compose.test.yml run tests pytest -v app/tests/test_tasks_*.py