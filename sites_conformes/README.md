# sites_conformes

Package Python pour Sites Conformes, un gestionnaire de contenu permettant de créer et gérer un site internet basé sur le Système de design de l'État (DSFR), accessible et responsive.

Ce package est généré automatiquement à partir du projet [Sites Faciles](https://github.com/numerique-gouv/sites-faciles) officiel.

## Installation

```bash
pip install sites_conformes
```

Ou avec poetry :

```bash
poetry add sites_conformes
```

## Utilisation

Ajoutez les applications à votre `INSTALLED_APPS` dans `settings.py` :

```python
INSTALLED_APPS = [
    # ... vos autres apps
    "dsfr",
    "sites_conformes",
    "sites_conformes.blog",
    "sites_conformes.core",
    "sites_conformes.events",
    "wagtail.contrib.settings",
    "wagtail.contrib.typed_table_block",
    "wagtail.contrib.routable_page",
    "wagtail_modeladmin",
    "wagtailmenus",
    "wagtailmarkdown",
]
```

Ajoutez les context processors nécessaires :

```python
TEMPLATES[0]["OPTIONS"]["context_processors"].extend(
    [
        "wagtailmenus.context_processors.wagtailmenus",
        "sites_conformes.core.context_processors.skiplinks",
        "sites_conformes.core.context_processors.mega_menus",
    ]
)
```

Configurez les URLs dans votre `urls.py` :

```python
# Option 1 : Utiliser directement la configuration d'URLs de sites_conformes (recommandé)
from sites_conformes.config.urls import *

# Option 2 : Configuration personnalisée
# Si vous avez besoin de personnaliser les URLs, vous pouvez copier le contenu
# de sites_conformes.config.urls et l'adapter à vos besoins
```

## Migration depuis Sites Faciles

Si vous migrez un site existant depuis le dépôt Sites Faciles vers ce package, vous devez mettre à jour les références ContentType dans votre base de données.

### Étapes de migration

1. **Installez le package** comme décrit ci-dessus et ajoutez toutes les applications à `INSTALLED_APPS`

2. **Exécutez les migrations Django** pour créer les nouveaux ContentTypes :
   ```bash
   python manage.py migrate
   ```

3. **Migrez les ContentTypes existants** :
   ```bash
   python manage.py migrate_contenttype
   ```

   Cette commande va :
   - Identifier tous les ContentTypes de l'ancienne structure (blog, events, forms, core, config)
   - Mettre à jour toutes les pages Wagtail pour pointer vers les nouveaux ContentTypes
   - Supprimer les anciens ContentTypes

4. **Vérifiez la migration** (optionnel - mode dry-run) :
   ```bash
   python manage.py migrate_contenttype --dry-run
   ```

### Pourquoi cette migration est nécessaire

Lorsque vous renommez des applications Django (par exemple de `blog` à `sites_conformes_blog`), Django crée de nouveaux ContentTypes. Les pages Wagtail existantes référencent toujours les anciens ContentTypes, ce qui provoque l'erreur :

```
PageClassNotFoundError: The page 'xxx' cannot be edited because the model class
used to create it (blog.blogindexpage) can no longer be found in the codebase.
```

La commande `migrate_contenttype` résout ce problème en mettant à jour toutes les références.

## Documentation

Pour plus d'informations sur l'utilisation de Sites Faciles, consultez la [documentation officielle](https://github.com/numerique-gouv/sites-faciles).

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## Crédits

Ce package est basé sur [Sites Faciles](https://github.com/numerique-gouv/sites-faciles) développé par la DINUM.
