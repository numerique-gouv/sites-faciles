# Onboarding tech

## Installation

Le projet peut se lancer en local ou avec Docker.

Dans le cas d’une installation en local, voir la section « Préparation de l’environnement de travail » ci-dessous.

### Dans tous les cas, copier les variables d’environnement

- Copier le fichier

```sh
cp .env.example .env
```

- Générer la `SECRET_KEY`

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- Mettre les valeurs pertinentes dans le fichier `.env`, notamment :
  - `DEBUG=True`
  - `HOST_PROTO=http`


### En local
#### Variables d’environnement

- mettre la variable d’environnement `USE_POETRY` à `1` dans le fichier `.env`
- il est possible de configurer l’envoi des emails vers la console Django (cf. [CONTRIBUTING.md](./CONTRIBUTING.md))

#### Installer le projet

- La commande suivante installe les dépendances, fait les migrations et collecte les fichiers

```sh
make init-dev
```

#### Créer un utilisateur

- La commande suivante crée un utilisateur administrateur avec tous les droits:

```
poetry run python manage.py createsuperuser
```

#### Lancer le serveur

```sh
make runserver
```

### via Docker
#### Lancer les containers

```sh
docker compose up
```

## Préparation de l’environnement de travail
Procédure testée sous Ubuntu.

### Prérequis

Installer :

* [Python 3](https://www.python.org/) (normalement déjà installé sur un système moderne)
* [git](https://git-scm.com/)
* [pipx](https://pipx.pypa.io/stable/)
* [poetry](https://python-poetry.org/)
* [just](https://just.systems/)
* [npm](https://docs.npmjs.com/)
* [gettext](https://www.gnu.org/software/gettext/gettext.html)

Sous Ubuntu, la commande pour cela est :

```sh
sudo apt install -y git python3 pipx just gettext
pipx ensurepath
pipx install poetry
```

Note : `sass` est appelé via [libsass](https://sass.github.io/libsass-python/) et il ne devrait donc pas y avoir besoin d’installer `ruby-sass`.

### Cloner le dépôt

```sh
git clone https://github.com/numerique-gouv/sites-faciles.git

# ou en ssh
git clone git@github.com:numerique-gouv/sites-faciles.git
```

Et rentrer dans le dossier du dépôt

```sh
cd sites-faciles
```

### PostgreSQL (base de données)

Avoir un PostgreSQL qui tourne en local (cf. procédure d’installation sur [Ubuntu](https://documentation.ubuntu.com/server/how-to/databases/install-postgresql/index.html) ou sur [Mac](https://postgresapp.com/).)

```sh
# créer un utilisateur
psql -c "CREATE USER sitesfaciles WITH CREATEDB PASSWORD 'votre_mot_de_passe';" -U postgres


# créer la base de données (vide pour l’instant)
psql -c "CREATE DATABASE sitesfaciles OWNER sitesfaciles;" -U postgres
```

