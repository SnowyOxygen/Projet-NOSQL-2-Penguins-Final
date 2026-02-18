# 🐧 Aide Projet – Classification des Manchots Palmer

## 👤 Contexte

Vous êtes analyste de données pour un centre de recherche en biologie marine.

**Votre mission** est d'étudier un jeu de données sur les manchots observés en Antarctique afin de :
- Comprendre leurs caractéristiques morphologiques
- Identifier des indicateurs pertinents permettant de distinguer les espèces
- Créer un modèle statistique ou prédictif pour analyser les données

---

## 📋 Description du Dataset

| Variable | Description |
|----------|-------------|
| `species` | Espèce (Adelie, Chinstrap, Gentoo) |
| `island` | Île d'observation |
| `bill_length_mm` | Longueur du bec (mm) |
| `bill_depth_mm` | Profondeur du bec (mm) |
| `flipper_length_mm` | Longueur des nageoires (mm) |
| `body_mass_g` | Masse corporelle (g) |
| `sex` | Sexe |
| `year` | Année de collecte |

---

## 📊 Partie 1 – Analyse Statistique Descriptive

### Objectifs
1. Explorer le jeu de données : nombre d'observations, types de variables, valeurs manquantes
2. Calculer les indicateurs descriptifs pour les variables numériques : moyenne, médiane, minimum, maximum, variance
3. Compter le nombre de manchots par espèce, par île et par sexe
4. Identifier les variables les plus discriminantes entre espèces
5. Interpréter les résultats et noter toute observation pertinente pour la suite du TP

### Questions à traiter
- Quelles espèces semblent surreprésentées dans le jeu de données ?
- Existe-t-il des différences marquées de taille, de masse ou de bec entre les espèces ?

---

## 🎨 Partie 2 – Visualisation des Données

### Objectifs
1. Créer des graphiques pour visualiser la distribution de chaque variable numérique
   - Histogrammes
   - Boxplots
   - Densité

2. Réaliser des scatter plots pour observer les relations entre :
   - Longueur et profondeur du bec, par espèce
   - Longueur des nageoires et masse corporelle, par sexe

3. Construire une matrice de corrélation pour toutes les variables numériques

4. Identifier visuellement les relations les plus fortes entre variables

### Questions à traiter
- Quelles variables semblent fortement corrélées ?
- Existe-t-il des biais visuels à prendre en compte lors de l'interprétation des graphiques ?
- Quelles observations pourraient aider à distinguer les espèces ?

---

## 📈 Partie 3 – Régression Simple et Multiple

### Objectifs
1. Mettre en place une régression linéaire simple pour prédire la masse corporelle à partir d'une seule variable
2. Étendre la régression à un modèle multiple en utilisant 2 ou 3 variables explicatives
3. Interpréter les résultats : coefficients, résidus, R², p-values
4. Vérifier les hypothèses de la régression :
   - Linéarité
   - Normalité des résidus
   - Homoscédasticité

### Questions à traiter
- Quels paramètres influencent le plus la masse corporelle des manchots ?
- Le modèle multiple améliore-t-il la prédiction par rapport au modèle simple ?
- Les hypothèses de la régression sont-elles respectées ?

---

## 🤖 Partie 4 – Classification Supervisée et Extraction d'Indicateurs

### Objectifs
1. Sélectionner les variables explicatives pour prédire l'espèce
2. Proposer une méthode de classification (ex. k-NN, Random Forest, arbre de décision) et justifier votre choix
3. Évaluer la performance du modèle à l'aide de critères tels que :
   - Précision
   - Matrice de confusion
   - Autres indicateurs pertinents
4. Créer un prototype d'application interactive permettant de :
   - Choisir une variable à visualiser
   - Afficher sa distribution (histogramme ou boxplot)
   - Visualiser la corrélation avec d'autres variables

### Questions à traiter
- Quelles espèces sont les plus difficiles à prédire et pourquoi ?
- Quelles variables sont les plus discriminantes pour la classification ?
- Quels indicateurs statistiques sont les plus pertinents pour ce dataset ?

---

## ✅ Résumé des Étapes

| Étape | Description | Livrables |
|-------|-------------|-----------|
| **1. EDA** | Analyse exploratoire et statistique | Statistiques descriptives, observations clés |
| **2. Visualisation** | Graphiques et corrélations | Plots, matrices de corrélation |
| **3. Régression** | Modèles prédictifs simples et multiples | Modèles entraînés, interprétations |
| **4. Classification** | Modèles de classification + prototype interactif | Modèle optimal, application interactive |
