# Experment

Ce dossier contient une vraie mini-application Python construite au-dessus d'EcoCode.

## Fichier principal

- `app.py` : charge un petit jeu de donnees, profile deux implementations, compare leurs emissions estimees, genere des rapports texte et HTML, puis appelle aussi la CLI EcoCode.

## Fonctionnalites EcoCode utilisees

- `carbon_profiler`
- `profile_callable`
- `eco_compare`
- `eco_report`
- `get_runtime_config`
- `render_html_report`
- CLI `ecocode config`
- CLI `ecocode report`
- CLI `ecocode compare`

## Lancer l'application

Depuis la racine du projet :

```bash
python experment/app.py
```

## Sorties generees

Lors de l'execution, l'application ecrit des artefacts dans `experment/output/` :

- un rapport texte,
- un rapport HTML,
- un JSON de comparaison,
- un rapport HTML genere via la CLI.

Le dossier de sortie est ignore par Git.