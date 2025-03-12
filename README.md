# Sites Faciles - Expérimentation sous forme de package

Sites Faciles est un gestionnaire de contenu permettant de créer et gérer un site internet basé sur le Système de design de l'État, accessible et responsive.
Développé sous forme de site Wagtail, il n'est à l'heure actuelle pas possible de l'utiliser comme dépendance d'un projet Wagtail existant.

Le projet courant vise cet objectif.

C'est un soft-fork, au sens où aucune fonctionnalité ne sera ajoutée via Sites Faciles dans ce fork.
Cependant une synchronisation directe des deux dépôts n'est pas possible car l'empaquetage de Sites Faciles nécessite de déplacer des fichiers, ce qui fausse la synchronisation.

Un script de synchronisation a donc été écrit qui vise à :
- déplacer l'arborescence dans un sous-dossier
- namespacer tout ce qui doit l'être dans le code source de Sites Faciles

---

Pour l'utilisation de Sites Faciles, voir le [README](./sites_faciles/README.md) original.

---

Le versionning et les tags suit de manière iso ceux de Sites Faciles.

## 🙋‍♂️ Comment tester 

**Pour le tester dans un projet wagtail existant** (⚠ c'est hautement expérimental, à ne tester que sur un projet local) :
- `poetry add sites-faciles-experiment` ou `pip install sites-faciles-experiment`
- ajouter quelques **settings** nécessaires au bon fonctionnement du projet, à savoir 
```py
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # ...
                "wagtailmenus.context_processors.wagtailmenus",
                "sites_faciles.content_manager.context_processors.skiplinks",
                "sites_faciles.content_manager.context_processors.mega_menus",
            ],
        },
    },
]

INSTALLED_APPS.extend(
    [
        "sites_faciles",
        "sites_faciles.blog",
        "sites_faciles.content_manager",
        "sites_faciles.events",
        "sass_processor",
        "wagtail.contrib.settings",
        "wagtail_modeladmin",
        "wagtailmenus",
        "wagtailmarkdown",
    ]
)

STATICFILES_FINDERS.extend([
    "sass_processor.finders.CssFinder",
])
```  
- Éventuellement **overrider le template de base de Sites Faciles** pour utiliser directement les modèles de page proposés
```html
{# sites_faciles/base.html #}

{% extends "votre_wagtail_existant/base.html" %}

{# Fournir un block content dans lequel les modèles de pages de sites faciles peuvent render le contenu #}
{% block content %}{% endblock %}
```
- Sinon utiliser le **champ streamfield sur un modèle existant**
```py 
# models.py 
from sites_faciles.content_manager.blocks import STREAMFIELD_COMMON_BLOCKS

# ... 

class CMSPage(Page):
    body = StreamField(
        STREAMFIELD_COMMON_BLOCKS,
        blank=True,
        use_json_field=True,
    )
```

- Voir la PR en cours côté [quefairemesdechets / longue vie aux objets](https://github.com/incubateur-ademe/quefairedemesobjets/pull/1375/files) pour l'ajout de wagtail + sites faciles à un projet Django

## 🔍 Quelques infos / observations en vrac 

- On a fait une solution _quick&dirty_ pour évaluer la faisabilité, on récupère **tout** : les modèles, les templates etc
- Idéalement il serait intéressant de pouvoir importer que le champ streamfield avec le rendering qui va bien, mais comme de nombreux blocs dépendent de `blog` et `event`, on se retrouve à devoir ajouter ces apps. Donc à voir pour rendre ça plus modulaire 
- Il y a un certains nombres de dépendances nécessaires à Sites Faciles qui sont normalement gérées par le wagtail existant qui accueille `sites-faciles-experiment` : `gunicorn`, `dj-database-url`...
- La dépendance à sass semble superflue, pourrait-on imaginer s'en passer ?

## ✅ Reste à faire 

- [ ] Voir comment rendre une éventuelle refacto rétro compatible avec les sites déjà déployés
- [ ] Rendre le streamfield de `content_manager` plus modulaire pour le rendre utilisable sans les dépendances aux apps blog et event
- [ ] Définir le scope
  - [ ] SSO / proconnect ? 
  - [ ] Streamfield
  - [ ] Modèles de page
  - [ ] Config wagtail
