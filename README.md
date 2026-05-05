# EcoCode

![CI](https://github.com/YANNBEN2310/ecocode-py/actions/workflows/ci.yml/badge.svg)

EcoCode est un package Python qui mesure une estimation de l'empreinte d'execution d'une fonction, propose quelques suggestions d'eco-conception via analyse statique, compare plusieurs implementations, et genere des rapports reutilisables en texte, JSON et HTML.

Le facteur carbone n'est pas fixe : il est paramétrable soit directement avec `carbon_intensity=...` en Python, soit avec `--carbon-intensity ...` dans la CLI, soit globalement avec la variable d'environnement `ECOCODE_CARBON_INTENSITY`.

## Etat actuel du projet

Le projet n'est plus seulement une idee ou un brouillon. A ce stade, EcoCode contient deja :

- un decorateur `carbon_profiler`,
- une API bas niveau `profile_callable`,
- une comparaison de fonctions avec `eco_compare`,
- des rapports texte, JSON et HTML,
- une CLI `ecocode` avec les commandes `report` et `compare`,
- une petite base de regles AST pour suggerer des ameliorations,
- une suite de tests `pytest`,
- une CI GitHub Actions,
- une licence MIT.

## Fonctionnalites deja implementees

### 1. Mesure d'empreinte a l'execution

EcoCode mesure aujourd'hui :

- le temps d'execution,
- le temps CPU,
- le pic memoire,
- une estimation d'energie,
- une estimation d'emissions CO2e.

Si `codecarbon` est installe, EcoCode peut s'appuyer dessus. Sinon, le package utilise un modele interne de secours base sur le temps CPU, la memoire et une intensite carbone configurable.

Ordre de priorite actuel pour le facteur carbone :

1. valeur passee explicitement a l'API ou a la CLI,
2. variable d'environnement `ECOCODE_CARBON_INTENSITY`,
3. valeur de secours interne du package.

### 2. Suggestions d'optimisation

Le module d'analyse statique detecte deja quelques patterns Python simples :

- `range(len(...))` quand une iteration directe serait suffisante,
- certaines list comprehensions identitaires inutiles,
- `sum([...])` quand une expression generatrice evite une liste intermediaire.

Ce n'est pas encore un moteur d'optimisation complet, mais la base existe et fonctionne.

### 3. Comparaison de plusieurs implementations

`eco_compare` permet deja de comparer deux fonctions avec les memes entrees. La CLI expose aussi cette fonctionnalite avec `ecocode compare ...`.

### 4. Rapports exportables

Ce point est deja fait.

EcoCode sait produire :

- un rapport texte lisible,
- une sortie JSON exploitable en CI,
- un rapport HTML exportable dans un fichier.

### 5. Integration CLI

Ce point est deja fait.

La commande `ecocode` est installee via `pyproject.toml` et permet aujourd'hui :

- `ecocode report ...`
- `ecocode compare ...`

### 6. Qualite projet

Ce point est deja en place aussi :

- tests `pytest`,
- CI GitHub Actions sur `push` et `pull_request`,
- structure de package propre,
- licence MIT.

## Ce qui n'est pas encore implemente

Ces parties de l'idee initiale ne sont pas encore developpees :

- plugin linter `green_linter`,
- cache carbone `carbon_aware_cache`,
- source externe d'intensite carbone en temps reel,
- historique de rapports ou persistence,
- integrations FastAPI, Flask, pytest plugin dedie, VS Code extension,
- blocage automatique de PR sur seuil carbone,
- modele d'analyse avance ou suggestions basees sur IA.

## Installation

Installation locale :

```bash
pip install -e .
```

Installation developpeur :

```bash
pip install -e .[dev]
```

Dependance optionnelle pour un suivi d'emissions plus realiste :

```bash
pip install codecarbon
```

## API Python

Exemple rapide :

```python
import os

from ecocode import CARBON_INTENSITY_ENV_VAR, carbon_profiler, eco_compare, eco_report


carbon_intensity = float(os.getenv(CARBON_INTENSITY_ENV_VAR, "55"))


@carbon_profiler(carbon_intensity=carbon_intensity)
def sum_loop(values):
    total = 0
    for index in range(len(values)):
        total += values[index]
    return total


def sum_builtin(values):
    return sum(values)


data = list(range(50_000))
sum_loop(data)

comparison = eco_compare(sum_loop, sum_builtin, data, carbon_intensity=carbon_intensity)
print(comparison.summary())

print(eco_report(sum_loop, data, carbon_intensity=carbon_intensity))
```

API principale exposee par le package :

- `carbon_profiler`
- `profile_callable`
- `eco_compare`
- `eco_report`

## CLI

Apres installation du package :

```bash
pip install -e .
```

Optionnellement, on peut fixer une valeur par defaut pour toute la session :

```bash
set ECOCODE_CARBON_INTENSITY=55
```

Rapport texte :

```bash
ecocode report ecocode.sample_targets:sum_loop --arg "[1, 2, 3]" --carbon-intensity 55
```

Rapport JSON :

```bash
ecocode report ecocode.sample_targets:sum_loop --arg "[1, 2, 3]" --carbon-intensity 55 --format json
```

Rapport HTML dans un fichier :

```bash
ecocode report ecocode.sample_targets:sum_loop --arg "[1, 2, 3]" --carbon-intensity 55 --format html --output reports/ecocode-report.html
```

Comparaison texte :

```bash
ecocode compare ecocode.sample_targets:sum_loop ecocode.sample_targets:sum_builtin --arg "[1, 2, 3]" --carbon-intensity 55
```

Comparaison JSON :

```bash
ecocode compare ecocode.sample_targets:sum_loop ecocode.sample_targets:sum_builtin --arg "[1, 2, 3]" --carbon-intensity 55 --format json
```

Format attendu pour les cibles : `module:function`.

Notes utiles :

- le module cible doit etre importable,
- `--arg` utilise `ast.literal_eval` pour parser des litteraux Python simples,
- `--format json` est pratique pour la CI,
- `--format html --output ...` permet de partager un rapport lisible,
- le facteur carbone peut etre passe en argument, ou defini via `ECOCODE_CARBON_INTENSITY`,
- `python -m ecocode.cli ...` fonctionne aussi si le package est installe, ou avec `PYTHONPATH=src` en local.

## Structure du projet

- `src/ecocode/profiler.py` : mesures runtime, estimation carbone, decorateur, structure `CarbonResult`
- `src/ecocode/static_analysis.py` : regles AST et suggestions
- `src/ecocode/compare.py` : comparaison entre deux implementations
- `src/ecocode/report.py` : rendu texte et HTML des rapports
- `src/ecocode/cli.py` : interface en ligne de commande
- `src/ecocode/sample_targets.py` : petites cibles d'exemple pour la CLI et les tests
- `tests/test_ecocode.py` : couverture fonctionnelle du prototype
- `.github/workflows/ci.yml` : CI GitHub Actions

## Exemple local

Un exemple plus complet est disponible dans `examples/basic_usage.py`.

Execution :

```bash
python examples/basic_usage.py
python -m pytest
```

## Tests et CI

Les tests se lancent localement avec :

```bash
python -m pytest
```

Le depot contient une CI GitHub Actions qui execute ces tests automatiquement sur chaque `push` et `pull_request`.

## Limites actuelles

- les chiffres sont des estimations, pas des mesures physiques exactes,
- l'analyse statique est volontairement simple,
- les regles actuelles couvrent seulement quelques patterns Python,
- la comparaison reste limitee a deux callables et a des arguments simples,
- il n'y a pas encore de persistence, de tableau de bord ou de source carbone externe.

## Roadmap realiste

1. Ajouter plus de regles AST pertinentes.
2. Ajouter `--output` sur plus de sous-commandes, notamment `compare`.
3. Ajouter un export Markdown ou un format machine-readable plus riche.
4. Connecter une source externe d'intensite carbone.
5. Ajouter des integrations framework et CI plus poussees.