def skiplinks(request):
    return {
        "skiplinks": [
            {"link": "#content", "label": "Contenu"},
            {"link": "#fr-navigation", "label": "Menu"},
        ]
    }
