HEROKU_APP=tesis-cabal-cugno-moreyra-back# FIXME: CHANGE THIS

git-hooks-setup:
	chmod +x git-hooks/pre-commit
	git config core.hooksPath git-hooks/

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

django-seed-db-prod:
	docker-compose exec web python manage.py loaddata fixtures/prod_dump.json
	docker-compose exec web python manage.py create_admin_superuser

django-seed-db-only-user:
	docker-compose exec web python manage.py loaddata fixtures/only_with_admin_user.json
	docker-compose exec web python manage.py create_admin_superuser

django-seed-db-users-and-domain:
	docker-compose exec web python manage.py loaddata fixtures/with_users_and_domain.json
	docker-compose exec web python manage.py create_admin_superuser

django-makemigrations:
	docker-compose exec web python manage.py makemigrations
	make docker-compose-web-change-files-ownership

django-migrate:
	docker-compose exec -T web python manage.py migrate

django-test:
	docker-compose exec -T web python manage.py test

django-build-prod:
	docker-compose -f compose-prod.yml build

django-run-prod:
	docker-compose -f compose-prod.yml up

django-run-prod-detached:
	docker-compose -f compose-prod.yml up -d

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

deploy:
	docker-compose stop
	git checkout master
	git pull
	make django-build-prod
	make django-run-prod-detached
	make django-migrate
	echo "Successfully deployed!!!!!! ✅✅✅"

## Shortcuts

dk-up: docker-compose-up
dk-web-out: docker-compose-get-web-output
