HEROKU_APP=tesis-cabal-cugno-moreyra-back# FIXME: CHANGE THIS

git-hooks-setup:
	chmod +x git-hooks/pre-commit
	git config core.hooksPath git-hooks/

help:
	@echo "See the sources"

build-and-deploy:
	docker-compose -f docker-compose.yml build
	docker tag backend_worker-beat registry.heroku.com/$(HEROKU_APP)/worker-beat
	docker push registry.heroku.com/$(HEROKU_APP)/worker-beat
	docker tag web registry.heroku.com/$(HEROKU_APP)/web
	docker push registry.heroku.com/$(HEROKU_APP)/web
	heroku container:release web worker-beat -a $(HEROKU_APP)

container-ssh:
	docker-compose exec web sh

container-worker-ssh:
	docker-compose exec worker-beat sh

docker-compose-up:
	docker-compose -f docker-compose.yml up

docker-compose-up-d:
	docker-compose -f docker-compose.yml up -d

docker-compose-build:
	docker-compose -f docker-compose.yml build

docker-compose-get-web-output:
	docker-compose logs -f web

docker-compose-get-all-containers-output:
	docker-compose logs -f web postgres

docker-compose-web-change-files-ownership:
	docker-compose exec web chown 1000:1000 -R .

heroku-ssh:
	heroku run sh -a $(HEROKU_APP)

heroku-logs:
	heroku logs --tail -a $(HEROKU_APP)

django-seed-db:
	docker-compose exec web python manage.py loaddata fixtures/prod_dump.json

django-makemigrations:
	docker-compose exec web python manage.py makemigrations
	make docker-compose-web-change-files-ownership

django-migrate:
	docker-compose exec web python manage.py migrate

django-test:
	docker-compose exec -T web python manage.py test

django-flush:
	docker-compose exec -T web python manage.py flush

python-lint:
	docker-compose exec -T web flake8

git-pre-commit:
	make python-lint
	make django-test

ci-run-tests:
	docker-compose exec -T web flake8 .
	docker-compose exec -T web python wait_for_postgres.py
	docker-compose exec -T web ./manage.py test

## Shortcuts

dk-up: docker-compose-up
dk-web-out: docker-compose-get-web-output
