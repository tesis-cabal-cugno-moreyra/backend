HEROKU_APP=tesis-cabal-cugno-moreyra-back# FIXME: CHANGE THIS

git-hooks-setup:
	chmod +x git-hooks/pre-commit
	git config core.hooksPath git-hooks/

help:
	@echo "See the sources"

build-and-deploy:
	docker-compose --env-file /dev/null -f docker-compose.yml build
	docker tag web registry.heroku.com/$(HEROKU_APP)/web
	docker push registry.heroku.com/$(HEROKU_APP)/web
	heroku container:release web -a $(HEROKU_APP)

container-ssh:
	docker-compose exec web sh

docker-compose-up-d:
	docker-compose --env-file /dev/null -f docker-compose.yml up -d

heroku-ssh:
	heroku run sh -a $(HEROKU_APP)

heroku-logs:
	heroku logs --tail -a $(HEROKU_APP)

django-makemigrations:
	docker-compose exec web python manage.py makemigrations

django-migrate:
	docker-compose exec web python manage.py migrate

django-test:
	docker-compose exec -T web python manage.py test

python-lint:
	docker-compose exec -T web flake8

git-pre-commit:
	make python-lint
	make django-test