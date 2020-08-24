# backend

[![Build Status](https://travis-ci.org/tesis-cabal-cugno-moreyra/backend.svg?branch=master)](https://travis-ci.org/tesis-cabal-cugno-moreyra/backend)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Backend for sicoin. Check out the project's [documentation](http://tesis-cabal-cugno-moreyra.github.io/backend/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  

# Local Development

Configure local git hooks (for tests and lint on pre-commits):
```bash
make git-hooks-setup
```

Start the dev server for local development:
```bash
make docker-compose-up-d
```

Run a command inside the docker container:

```bash
docker-compose run --rm web [command]
```
or, if you want a Console inside the web container (using sh)
```bash
make container-ssh
```

Create new migrations:
```bash
make django-makemigrations
```

Run migrations:
```bash
make django-migrate
```
