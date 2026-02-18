# Projet 2 — Classification des Penguins et Benchmark Multi-NoSQL

## Description du projet

**Classification d'espèces de manchots avec MongoDB vs Cassandra et optimisation scalable**

---

## 📊 Dataset officiel

- [Palmer Penguins Dataset](https://allisonhorst.github.io/palmerpenguins/)
- [Kaggle — Penguins Dataset](https://www.kaggle.com/datasets/parulpandey/palmer-archipelago-antarctica-penguin-data)

---

## 🎯 Contexte et problématique métier

Un institut écologique souhaite **classifier automatiquement des espèces de manchots en Antarctique** à partir de mesures biométriques.

### Espèces à prédire
- **Adelie**
- **Chinstrap**
- **Gentoo**

---

## 📚 Objectifs pédagogiques

Ce projet vise à :
- Comparer deux moteurs NoSQL (document vs colonne distribuée)
- Analyser la scalabilité et la performance
- Appliquer des stratégies avancées (partitionnement, cache)
- Intégrer Spark pour le traitement distribué

---

## 🛠️ Travail demandé

### 1. Classification supervisée

#### Variables d'entrée
- `bill_length_mm`
- `bill_depth_mm`
- `flipper_length_mm`
- `body_mass_g`

#### Sortie attendue
- `species`

---

### 2. Modélisation multi-NoSQL

#### Modèle MongoDB (document)

```json
{
  "penguin_id": "P1001",
  "features": {
    "bill_length": 46.2,
    "bill_depth": 14.5,
    "flipper_length": 210,
    "body_mass": 5000
  },
  "label": "Gentoo",
  "island": "Biscoe"
}
```

#### Modèle Cassandra (colonne distribuée)

```sql
CREATE TABLE penguins_by_island (
  island TEXT,
  species TEXT,
  penguin_id UUID,
  bill_length FLOAT,
  body_mass INT,
  PRIMARY KEY ((island), species, penguin_id)
);
```

---

### 3. Benchmark comparatif MongoDB vs Cassandra

#### Métriques à mesurer
- Latence moyenne (ms)
- Throughput (requêtes/seconde)
- Scalabilité (augmentation du volume de données)
- Consommation mémoire (MB)

#### Exemple de synthèse attendue

| Critère | MongoDB | Cassandra |
|---------|---------|-----------|
| Lecture ML | Très bon | Excellent |
| Scalabilité massive | Moyen | Excellent |
| Requêtes analytiques | Excellent | Bon |

---

### 4. Optimisation avancée

- **Partitionnement Cassandra** par île
- **Index MongoDB** sur species
- **Cache Redis** pour prédictions récentes

---

### 5. Intégration Spark MLlib

- Entraînement distribué
- Classification batch
- Stockage des résultats dans MongoDB et Cassandra

---

## 📦 Livrables attendus

- ✅ Modèles MongoDB + Cassandra (schémas optimisés)
- ✅ Modèle ML de classification (Random Forest, KNN, Decision Tree)
- ✅ Stratégie de Partitionnement/Sharding MongoDB implémentée avec benchmarks
- ✅ Optimisations d'indexation (avant/après sharding)
- ✅ Benchmarks comparatifs complets (latence, throughput, mémoire)
- ✅ Intégration Fullstack (Backend FastAPI + Frontend React opérationnel)
- ✅ Pipeline Big Data (entraînement → stockage → prédiction)
- ✅ Rapport technique complet avec justifications d'architecture et benchmarks
