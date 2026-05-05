# EcoCode

![CI](https://github.com/YANNBEN2310/ecocode-py/actions/workflows/ci.yml/badge.svg)

EcoCode est un prototype Python qui estime l'empreinte d'execution d'une fonction et la combine avec quelques suggestions d'eco-conception basees sur l'analyse statique du code.

## Ce que contient ce prototype

- `carbon_profiler` : un decorateur qui execute une fonction, estime ses emissions et affiche un resume.
- `profile_callable` : une API bas niveau qui renvoie a la fois le resultat de la fonction et un objet structure avec les mesures.
- `eco_compare` : un utilitaire pour comparer deux implementations avec les memes entrees.
- `eco_report` : un generateur de rapport texte, pratique pour des logs CI ou pour une future exportation HTML/JSON.
- Des regles AST simples qui detectent quelques patterns Python potentiellement couteux en CPU ou en memoire.

## Installation locale

```bash
pip install -e .
```

Installation developpeur :

```bash
pip install -e .[dev]
```

Dependance optionnelle pour une mesure plus realiste des emissions :

```bash
pip install codecarbon
```

Si `codecarbon` n'est pas installe, EcoCode bascule sur un modele interne d'estimation fonde sur le temps CPU, la memoire et une intensite carbone configurable.

## Demarrage rapide

```python
from ecocode import carbon_profiler, eco_compare, eco_report


@carbon_profiler(carbon_intensity=55)
def sum_loop(values):
    total = 0
    for index in range(len(values)):
        total += values[index]
    return total


def sum_builtin(values):
    return sum(values)


data = list(range(50_000))
sum_loop(data)

comparison = eco_compare(sum_loop, sum_builtin, data, carbon_intensity=55)
print(comparison.summary())

print(eco_report(sum_loop, data, carbon_intensity=55))
```

## Structure du package

- `src/ecocode/profiler.py` : mesure runtime, modele de resultat, decorateur.
- `src/ecocode/static_analysis.py` : suggestions basees sur l'AST Python.
- `src/ecocode/compare.py` : comparaison entre deux fonctions.
- `src/ecocode/report.py` : mise en forme d'un rapport texte.
- `src/ecocode/__init__.py` : API publique exportee par le package.

## Exemple complet

Un exemple reutilisable est disponible dans `examples/basic_usage.py`.

Execution :

```bash
python examples/basic_usage.py
pytest
```

## Qualite et CI

Le depot contient une CI GitHub Actions qui execute automatiquement `pytest` sur chaque `push` et `pull request`.

Commande locale equivalente :

```bash
python -m pytest
```

Pour contribuer proprement, l'ordre minimal est :

1. installer les dependances de dev,
2. lancer les tests localement,
3. pousser la branche et verifier que la CI passe.

## CLI

EcoCode expose aussi une commande terminal `ecocode`.

Apres installation locale du package :

```bash
pip install -e .
```

Exemple :

```bash
ecocode report ecocode.sample_targets:sum_loop --arg "[1, 2, 3]" --carbon-intensity 55
```

Sortie JSON pour la CI ou un traitement automatique :

```bash
ecocode report ecocode.sample_targets:sum_loop --arg "[1, 2, 3]" --carbon-intensity 55 --format json
```

Comparaison de deux implementations :

```bash
ecocode compare ecocode.sample_targets:sum_loop ecocode.sample_targets:sum_builtin --arg "[1, 2, 3]" --carbon-intensity 55
```

Version JSON :

```bash
ecocode compare ecocode.sample_targets:sum_loop ecocode.sample_targets:sum_builtin --arg "[1, 2, 3]" --carbon-intensity 55 --format json
```

Format attendu pour la cible : `module:function`.

Notes :

- le module doit etre importable depuis le dossier courant,
- `--arg` accepte des litteraux Python simples evalues avec `ast.literal_eval`,
- `--format json` permet d'integrer plus facilement EcoCode dans une CI ou un autre outil,
- `python -m ecocode.cli ...` fonctionne aussi une fois le package installe, ou avec `PYTHONPATH=src` pendant un usage local non installe.

## Comment les developpeurs pourront l'utiliser plus tard

### En local pendant le developpement

- profiler une fonction critique avant une mise en production,
- comparer deux implementations avant de choisir la plus sobre,
- ajouter des rapports EcoCode dans une suite de benchmarks.

### En integration continue

- lancer des comparaisons sur les fonctions sensibles,
- serialiser les resultats en JSON,
- bloquer une PR si une regression carbone depasse un seuil.

### Dans des outils internes

- brancher EcoCode sur un service FastAPI ou Flask,
- l'integrer a un plugin VS Code,
- produire des rapports RSE sur des traitements batch ou data.

## Pistes d'evolution pour les developpeurs

### 1. Ameliorer le modele d'emissions

Remplacer le modele de secours par :

- des donnees de puissance CPU specifiques a la machine,
- des donnees d'intensite carbone regionales via API,
- des modeles adaptes a NumPy, Pandas, Polars ou aux charges ML.

### 2. Ajouter plus de regles statiques

Le visiteur AST est volontairement simple. Il peut etre etendu pour detecter :

- des boucles imbriquees sur de gros volumes,
- des listes temporaires inutiles,
- des copies repetitives de DataFrame,
- des concatenations de chaines dans des boucles,
- des acces I/O bloquants ou repetitifs.

### 3. Ajouter une CLI ou une API machine-readable

Prochaines evolutions naturelles :

- ajouter une CLI `ecocode run script.py`,
- exporter les rapports en JSON,
- generer des rapports HTML,
- stocker un historique des mesures.

### 4. Ajouter des integrations framework

Quelques directions utiles :

- middleware Flask ou FastAPI pour profiler les endpoints,
- helpers Jupyter pour notebooks,
- plugin pytest pour comparer des benchmarks,
- extension VS Code pour suggerer des corrections en direct.

## Limites actuelles du prototype

- Les chiffres sont des estimations, pas des mesures materielles exactes.
- Les suggestions sont basees sur des regles simples, pas sur un moteur IA.
- Le rapport est textuel uniquement.
- Il n'y a pas encore de couche de persistence ni de CLI.

## Roadmap conseillee

1. Ajouter des tests automatises.
2. Exporter les rapports en JSON et HTML.
3. Ajouter une CLI.
4. Brancher une source externe d'intensite carbone.
5. Etendre les regles AST et les integrations CI.