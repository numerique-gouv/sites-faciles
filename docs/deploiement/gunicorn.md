# Configurer le serveur applicatif (Gunicorn) — 🔵 Confirmé

[Gunicorn](https://gunicorn.org/) est le serveur qui exécute l’application
Django en production. Il reçoit les requêtes HTTP (directement, ou via Nginx ou
la plateforme d’hébergement), les confie à Django et renvoie les réponses.

Il est indispensable en production, où le serveur de développement de Django
(`runserver`) ne doit pas être utilisé. Gunicorn permet notamment :

- de **servir plusieurs visiteurs en même temps**, en répartissant les requêtes
  entre plusieurs processus ;
- de **garder le site disponible**, en relançant automatiquement un processus
  qui plante ou ne répond plus.

Il ne rend pas le chargement d’une page plus rapide en soi, mais ses réglages
déterminent combien de requêtes le site peut traiter à la fois : ils jouent
donc sur la réactivité du site lorsqu’il reçoit beaucoup de visites, et sur la
mémoire utilisée par le serveur.

Sites Conformes fournit une configuration prête à l’emploi : **la plupart des
instances n’ont rien à régler**. Cette page explique son fonctionnement et
comment l’adapter, notamment lorsque la mémoire du serveur est limitée.

(ou-se-trouve-la-configuration)=

## Où se trouve la configuration

La configuration se trouve dans le fichier
[`gunicorn.conf.py`](https://github.com/numerique-gouv/sites-conformes/blob/main/gunicorn.conf.py)
à la racine du dépôt. Gunicorn le charge **automatiquement** lorsqu’il est lancé
depuis ce dossier, quel que soit le mode de déploiement : `Procfile` sur
Scalingo, `entrypoint.sh` avec Docker, service systemd ou `just run_gunicorn`.

Les valeurs de ce fichier peuvent être modifiées par des variables
d’environnement `GUNICORN_*` (voir [Réglages](#reglages-gunicorn)), sans toucher
au code.

:::{note}
Les options passées **en ligne de commande** à Gunicorn sont prioritaires sur
le fichier `gunicorn.conf.py`. Par exemple, l’exemple de service systemd de la
page {doc}`serveur-linux` passe `--workers 3` : cette valeur remplace alors
`GUNICORN_WORKERS`. Ordre de priorité, du plus faible au plus fort :

1. `gunicorn.conf.py` (et donc les variables `GUNICORN_*` qu’il lit) ;
2. la variable `GUNICORN_CMD_ARGS`, si elle est définie ;
3. les options de la ligne de commande.
:::

## Fonctionnement

Gunicorn s’organise en deux niveaux :

```text
                 Processus maître
       (surveille, ne traite aucune requête)
             │                       │
         Worker 1                Worker 2         ← processus indépendants,
    (copie de l’application)  (copie de l’application)   chacun sa mémoire
       │       │                 │       │
    thread  thread            thread  thread      ← requêtes traitées
                                                    en même temps
```

- Le **processus maître** démarre les workers, les surveille et en relance un
  s’il plante ou ne répond plus.
- Les **workers** sont des processus Python complets, qui contiennent chacun une
  copie de Django, de Wagtail et du code du site. Ce sont eux qui traitent les
  requêtes.
- Les **threads** permettent à un worker de traiter plusieurs requêtes en même
  temps.

Le nombre de requêtes traitées simultanément est donc :
**nombre de workers × nombre de threads**.

:::{tip}
En Python, un seul thread d’un processus exécute du code à un instant donné.
Les threads n’accélèrent donc pas le calcul d’une page : ils sont utiles
pendant les **attentes** (requêtes à la base de données, appels à un service
externe), pendant lesquelles un autre thread peut avancer. Ils ne servent que
si le site reçoit souvent plusieurs requêtes en même temps.
:::

### Chargement anticipé de l’application

La configuration active `preload_app` : le processus maître charge
l’application **une seule fois**, puis crée les workers en se dupliquant. Les
workers démarrent ainsi plus vite, ce qui accélère les déploiements et les
redémarrages.

Au départ, les workers partagent la mémoire du processus maître. En Python, ce
partage diminue au fil du temps, car le simple fait d’utiliser un objet le
modifie en mémoire. Il faut donc compter qu’à terme, le processus maître et
chaque worker occupent chacun une copie de l’application.

(reglages-gunicorn)=

## Réglages

| Variable | Rôle | Défaut | Effet sur la mémoire |
| --- | --- | --- | --- |
| `GUNICORN_WORKERS` | Nombre de workers. À défaut, `WEB_CONCURRENCY` est utilisé (définie automatiquement par Scalingo). | `2` | **Fort** : chaque worker ajoute une copie complète de l’application. |
| `GUNICORN_THREADS` | Nombre de threads par worker, c’est-à-dire de requêtes qu’un worker traite en même temps. | `1` | **Fort sous charge** : chaque requête en cours occupe de la mémoire pendant la génération de la page. |
| `GUNICORN_TIMEOUT` | Délai (en secondes) au-delà duquel un worker qui ne répond plus est redémarré. | `120` | Aucun. |
| `GUNICORN_MAX_REQUESTS` | Nombre de requêtes traitées par un worker avant qu’il soit redémarré. | `10000` | **Bénéfique** : remet régulièrement la mémoire du worker à zéro. |
| `GUNICORN_MAX_REQUESTS_JITTER` | Aléa ajouté à `GUNICORN_MAX_REQUESTS`, pour que les workers ne redémarrent pas tous en même temps. | `2500` | Aucun. |

Deux réglages sont fixés dans le code et ne dépendent d’aucune variable :

- `worker_class = "gthread"` : workers capables d’utiliser des threads ;
- `preload_app = True` : chargement anticipé de l’application (voir
  ci-dessus).

## Mémoire et taille du serveur

La mémoire utilisée par Gunicorn dépend surtout du nombre de workers et du
nombre de requêtes traitées en même temps :

```text
mémoire ≈ processus maître
        + workers × (application + requêtes simultanées par worker × mémoire par requête)
```

La mémoire nécessaire varie selon la taille du site et le contenu des pages.
À titre d’exemple, sur une instance de production hébergée sur un conteneur
Scalingo de 1 Go, avec 2 workers :

| Threads par worker | Requêtes simultanées | Mémoire constatée |
| --- | --- | --- |
| 4 | 8 | environ 800 Mo, plus du swap : la limite était atteinte |
| 2 | 4 | environ 300 à 520 Mo selon le trafic, avec par moments un peu de swap |
| 1 | 2 | environ 450 Mo, sans swap |

Avec 2 threads, la mémoire dépasse déjà par moments 512 Mo : ce réglage
convient à un conteneur de 1 Go, mais pas à un conteneur de 512 Mo. C’est
pourquoi la valeur par défaut de `GUNICORN_THREADS` est `1` : elle convient
aussi aux petits conteneurs (512 Mo et moins).

### Recommandations

- **Gardez les valeurs par défaut** tant que le site fonctionne correctement.
- **Si la mémoire approche de la limite ou si le serveur utilise du swap**,
  réduisez d’abord le nombre de workers, par exemple `GUNICORN_WORKERS=1` sur
  un petit conteneur.
- **Si le site est lent sous forte affluence** et que la mémoire le permet,
  augmentez progressivement `GUNICORN_THREADS` ou `GUNICORN_WORKERS`, puis
  surveillez la mémoire pendant quelques heures de trafic normal.
- Après chaque changement, comparez la mémoire **juste après le redémarrage**
  et **après une à deux heures de trafic** : les threads n’occupent de mémoire
  que lorsque plusieurs requêtes arrivent en même temps.

## Modifier un réglage

### Sur Scalingo

Définissez la variable, puis **redémarrez l’application** : la modification
d’une variable n’est prise en compte qu’au démarrage suivant.

Depuis le tableau de bord Scalingo, ajoutez ou modifiez la variable dans
l’onglet **« Environnement »** de votre application (voir {doc}`scalingo`),
puis redémarrez l’application depuis le tableau de bord.

En ligne de commande, l’équivalent est :

```sh
scalingo --app mon-site env-set GUNICORN_THREADS=1
scalingo --app mon-site restart
```

Pour revenir à la valeur par défaut :

```sh
scalingo --app mon-site env-unset GUNICORN_THREADS
scalingo --app mon-site restart
```

La mémoire de l’application se suit dans le tableau de bord, onglet
**« Metrics »**, graphique **« Memory – web »** (mémoire, swap et limite du
conteneur).

### Sur un serveur Linux ou avec Docker

Ajoutez la variable au fichier `.env` de l’instance :

```sh
GUNICORN_THREADS=1
```

Puis redémarrez l’application, par exemple `sudo systemctl restart
sites-conformes` avec le service décrit dans {doc}`serveur-linux`.

Vérifiez aussi que la commande qui lance Gunicorn ne passe pas la même option
en ligne de commande, qui serait prioritaire (voir
[Où se trouve la configuration](#ou-se-trouve-la-configuration)).

## Voir aussi

- {doc}`variables-environnement`, section « Serveur applicatif (Gunicorn) » ;
- la [documentation de Gunicorn](https://docs.gunicorn.org/en/stable/settings.html)
  pour la liste complète des réglages ;
- la [taille des conteneurs Scalingo](https://doc.scalingo.com/platform/internals/container-sizes).
