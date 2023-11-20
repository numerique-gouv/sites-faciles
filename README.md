# Gestionnaire de contenu DSFR et Accessible

**Créez et gérez votre site internet simplement**

Gestionnaire de contenu (CMS) pour créer un site internet dont le domaine se terminant par .gouv.fr . Pas besoin de compétence technique pour mettre à jours le contenu.

**Un CMS basé sur la solution open source Wagtail**

Créez ou modifiez des pages, ajoutez un menu de navigation, des boutons, images, vidéos, contributeurs etc

**Système de Design de l'État**

Construisez vos pages à l'aide de composants prêts à l'emploi issus du Système de Design de l'État (DSFR)

**Accessible et responsive**

Le contenu des pages générées par le CMS est partiellement conforme selon la norme RGAA 4.1 et responsive





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

### Dans tous les cas, copier les variables d’environnement

```
cp .env.example .env
```

- Mettre une clef secrète et vérifier les autres valeurs

### En local
#### Installer poetry s’il ne l’est pas

Cf. la [documentation de poetry](https://python-poetry.org/docs/#installationok)

#### Installer les dépendances

```
poetry install
```

#### Lancer les migrations

```
python manage.py migrate
```

#### Lancer le serveur

```
poetry run python manage.py runserver
```

#### Effectuer les tests

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

#### Lancer les containers

```sh
docker compose up
```
