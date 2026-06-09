# Maison du Droit - Suivi & Gestion des Entretiens 🏛️

Ce projet est une application web construite avec **Streamlit** et **PostgreSQL** pour la gestion administrative, la saisie des entretiens, et le suivi statistique pour la Maison du Droit.

---

## 🚀 Installation & Exécution Locale

### 1. Prérequis
- Python 3.10+
- PostgreSQL installé et en cours d'exécution

### 2. Cloner le projet et installer les dépendances
```bash
git clone https://github.com/Nathanbzh/sae501.git
cd sae501
```

Créez un environnement virtuel et installez les dépendances :
```bash
# Création de l'environnement virtuel
python -m venv .venv

# Activation (Windows)
.venv\Scripts\activate
# Activation (macOS/Linux)
source .venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

### 3. Configuration de l'environnement
Copiez le fichier `.env.example` pour créer votre fichier `.env` de configuration locale :
```bash
cp .env.example .env
```
Éditez le fichier `.env` nouvellement créé et renseignez les identifiants de connexion de votre serveur PostgreSQL local.

### 4. Initialisation de la base de données
Placez vos fichiers Excel d'entretiens (ex: `janvier.xlsx`, `fevrier.xlsx`, etc.) dans le dossier `./data_entretien/` à la racine.

Exécutez ensuite les scripts d'initialisation et d'import :
```bash
# 1. Crée la base de données locale (si inexistante), génère les tables et les métadonnées
python creation_base.py

# 2. Lit les fichiers Excel de data_entretien/ et peuple la base de données
python alimentation_base.py
```

### 5. Lancer l'application
Démarrez le serveur local Streamlit :
```bash
streamlit run Accueil.py
```
L'application sera accessible dans votre navigateur à l'adresse [http://localhost:8501](http://localhost:8501).

---

## ☁️ Déploiement sur Render

Pour déployer l'application sur **Render**, suivez ces étapes :

### Étape 1 : Créer la base de données PostgreSQL sur Render
1. Connectez-vous sur votre dashboard [Render](https://render.com).
2. Cliquez sur **New** ➔ **PostgreSQL**.
3. Choisissez le forfait **Free** (gratuit).
4. Une fois créée, copiez les informations de connexion disponibles dans l'onglet **Connect** :
   - **Host** (Hôte)
   - **Database** (Nom de base)
   - **Username** (Utilisateur)
   - **Password** (Mot de passe)

### Étape 2 : Initialiser la base Render depuis votre machine locale
Puisque le forfait gratuit Render n'offre pas d'accès en ligne de commande directe persistant pour importer des fichiers lourds facilement, effectuez l'initialisation depuis votre terminal local connecté à la BDD Render :

1. Modifiez temporairement votre fichier `.env` local pour y mettre les paramètres **externes** de votre base de données Render.
2. Assurez-vous d'avoir placé les fichiers `.xlsx` sources dans le dossier `data_entretien/`.
3. Lancez les scripts de création et d'alimentation :
   ```bash
   python creation_base.py
   python alimentation_base.py
   ```
   *Note : Le script `creation_base.py` détectera que la base distante existe déjà et lancera directement la création des tables sans tenter de recréer la BDD globale (ce qui échouerait en raison des limites de droits sur Render).*
4. Une fois l'alimentation terminée, vous pouvez remettre vos accès locaux dans le fichier `.env`.

### Étape 3 : Déployer le service Streamlit
1. Sur Render, cliquez sur **New** ➔ **Web Service**.
2. Connectez votre dépôt GitHub `https://github.com/Nathanbzh/sae501.git`.
3. Configurez les champs suivants :
   - **Runtime** : `Python`
   - **Build Command** :
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command** :
     ```bash
     streamlit run Accueil.py --server.port $PORT --server.address 0.0.0.0
     ```
4. Allez dans l'onglet **Environment** du service web et ajoutez les variables d'environnement de la BDD Render (en utilisant les valeurs d'accès **internes** fournies par Render, plus rapides pour la communication entre le service web et la BDD) :
   - `DB_HOST`
   - `DB_PORT` : `5432`
   - `DB_USER`
   - `DB_PASS`
   - `DB_NAME`

Une fois le déploiement terminé, Render vous fournira l'URL publique de votre application !