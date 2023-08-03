ifeq ($(USE_VENV),1)
	EXEC_CMD :=
else
	EXEC_CMD := docker-compose exec -ti web
endif

.PHONY: web-prompt
web-prompt:
	$(EXEC_CMD) bash

.PHONY: test-unit
test-unit:
	$(EXEC_CMD) python manage.py test --settings config.settings_test

.PHONY: test-e2e
test-e2e:
	$(EXEC_CMD) python manage.py behave --settings config.settings_test

.PHONY: test
test: test-e2e test-unit

.PHONY: quality
quality:
	$(EXEC_CMD) black --check --exclude=venv .
	$(EXEC_CMD) isort --check --skip-glob="**/migrations" --extend-skip-glob="venv" .
	$(EXEC_CMD) flake8 --count --show-source --statistics --exclude=venv .

.PHONY: fix
fix:
	$(EXEC_CMD) black --exclude=venv .
	$(EXEC_CMD) isort --skip-glob="**/migrations" --extend-skip-glob="venv" .
