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

## Déploiement

Déploiement sur scalingo, on déploiera des VERSIONS plutôt sur des branches

### en preprod

```sh
git remote add qfdmo-preprod-cms SCALINGO_PREPROD_APP
git push qfdmo-preprod-cms VERSION:master
```

### en prod

```sh
git remote add qfdmo-preprod-cms SCALINGO_PROD_APP
git push qfdmo-cms VERSION:master
```
