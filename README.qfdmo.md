# Version spécifique aux site longuevieauxobjets.ademe.fr

Ce repo est un fork de [numerique-gouv/sites-faciles](https://github.com/numerique-gouv/sites-faciles)
Il permet de versionner des partie de documentation et de CI

## En plus dans ce fork

- La documentation ci-dessous à propos de 
- Les scripts de CI

## Github action

La github action [sync_prod_to_preprod.yml](.github/workflows/sync_prod_to_preprod.yml) permet de copier l'environnement de preprod vers la prod:

- copie de la base de données de prod vers la preprod
- execution des migrations en preprod
- copie du repo s3 de prod vers le repo s3 de preprod

Cette action est déclanchée à la demande [sur l'interface Github action](https://github.com/incubateur-ademe/qfdmo-sites-faciles/actions/workflows/sync_databases.yml)

Attention, un ensemble de `secret key` sont à configurer sur l'interface github pour l'execution de cette action.

## Mise à jour

On remettra régulièrement ce fork à jour à partir de [numerique-gouv/sites-faciles](https://github.com/numerique-gouv/sites-faciles)

Utiliser les boutons `Sync fork` sur l'interface de ce projet Github (cf. [syncing-a-fork](https://docs.github.com/fr/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)

synchroniser aussi les tags :

```sh
git remote add numerique-gouv/sites-faciles https://github.com/numerique-gouv/sites-faciles.git
git fetch numerique-gouv/sites-faciles --tags
```

## Déploiement

Déploiement sur scalingo, on déploiera des VERSIONS plutôt sur des branches

### en preprod

```sh
git remote add qfdmo-preprod-cms SCALINGO_PREPROD_APP
git push qfdmo-preprod-cms VERSION:master
```

### en prod

```sh
git remote add qfdmo-cms SCALINGO_PROD_APP
git push qfdmo-cms VERSION:master
```

### Copier les bases de données et fichiers d'un environnement à un autre

Télécharger et décompresser le backup de la base de données d'origine. Un fichier avec l'extension `*.pgsql` est disponible

```sh
DATABASE_URL=postgres://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>?sslmode=prefer
DUMP_FILE=<DUMP_FILE_NAME>.pgsql
for table in $(psql "${DATABASE_URL}" -t -c "SELECT \"tablename\" FROM pg_tables WHERE schemaname='public'"); do
     psql "${DATABASE_URL}" -c "DROP TABLE IF EXISTS \"${table}\" CASCADE;"
done
pg_restore -d "${DATABASE_URL}" --clean --no-acl --no-owner --no-privileges "${DUMP_FILE}"
```

Et si nécessaire, ne pas oublier de passer les migration sur lenvironnement cible

```sh
TARGETED_APP=<TARGETED_APP>
scalingo --region osc-fr1 --app $TARGETED_APP run python manage.py migrate
```

Copier les fichiers S3 si nécessaire

```sh
aws --profile qfdmoc_cms --endpoint-url https://cellar-c2.services.clever-cloud.com s3 sync --delete s3://<ORIGIN_S3> s3://<TARGET_S3>
```
