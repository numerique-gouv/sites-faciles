# Content Manager

## Prérequis

- Python 3.10
- Postgreql 14.x.

## Installer les pre-commit hooks

```
pre-commit install
```

On peut faire un premier test en faisant tourner :

```
pre-commit run --all-files
```

## Installation

Le projet peut se lancer en local ou avec Docker.

### En local

#### Créer un environnement virtuel

```
# Configurer et activer l'environnement virtuel
python -m venv venv
. venv/bin/activate

# Installer les packages requis
pip install -r requirements.txt
```

#### Copier les variables d'environnement

```
cp .env.example .env
```

#### Lancer le serveur

```
python manage.py runserver
```

#### Lancer les migrations

```
python manage.py migrate
```

#### Effectuer les tests

D'abord installer les dépendances de test :

```sh
pip install -r requirements.txt
```

Les tests unitaires peuvent être lancés avec `make test-units`, les
tests E2E avec `make test-e2e`, les deux avec `make test`.

Pour les tests E2E, si vous n'utilisez pas Docker, il vous faudra
[Firefox](https://www.mozilla.org/fr/firefox/download/thanks/) et
[`geckodriver`](https://github.com/mozilla/geckodriver/releases)
accessibles sur votre machine pour lancer les tests E2E.  Sur MacOS,
vous pouvez les installer via [brew](https://brew.sh/) avec la commande: `brew install geckodriver`.

Vous pouvez également générer un rapport sur la couverture de tests :
```sh 
coverage run manage.py test --settings config.settings_test
```

### via Docker

#### Copier les variables d'environnement

```sh
cp .env.example .env
```

#### Lancer les containers

```sh
docker-compose up
```
