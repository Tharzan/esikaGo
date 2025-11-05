# 🏠 EsikaGo – Digital Property & Rental Management Powered by Hedera

## 🌍 Overview

EsikaGo est une solution complète de **gestion numérique de la propriété et de la location** bâtie sur le réseau **Hedera Hashgraph**.

Elle permet aux propriétaires, locataires et investisseurs de gérer, signer et vérifier leurs transactions immobilières de manière **sécurisée, transparente et immuable** grâce à l'intégration des services Hedera.

EsikaGo sécurise l'**authentification numérique** des documents, simplifie la gestion locative (propriété, salons, restaurants), et introduit des méthodes efficaces pour contrer le phénomène de "no-show" (absentéisme) très fréquent en Afrique, en s'appuyant sur la technologie de Hedera et la **reconnaissance faciale**.

---

## 🛑 Problématiques Adressées en Afrique

L'Afrique fait face à plusieurs défis majeurs dans la gestion immobilière et commerciale :

* **Gestion Archaïque et Non-Traçable :** 📄 Gestion locative souvent manuelle, archaïque et manquant de traçabilité numérique, rendant les transactions non fiables.
* **Manque de Confiance pour la Diaspora :** ✈️ Forte dépendance à la présence physique ou aux proches, entraînant un manque de confiance pour les investisseurs et propriétaires vivant à l'étranger.
* **Perte de Revenus par le "No-Show" :** 📉 Problèmes d'optimisation de gestion et pertes de revenus considérables dans les secteurs de la restauration et des salons de beauté dus au non-respect des réservations.
* **Authentification Documentaire :** ❌ Absence d'authentification numérique formelle et sécurisée pour les documents légaux et les contrats.

---

## ✨ Nos Solutions et Technologies Clés

| Fonctionnalité | Description | Technologie Hedera |
| :--- | :--- | :--- |
| **Authentification de Documents** | Signature et ancrage immuable des quittances et contrats de location sur la blockchain. | **Hedera Consensus Service (HCS)** |
| **Sécurité des Transactions** | Utilisation de la **reconnaissance faciale** et de la **cryptographie** (clés privées) pour valider l'identité lors des actions critiques. | Cryptographie Asymétrique (Clés) |
| **Gestion Optimisée** | Simplification de la gestion des propriétés, des paiements, et des réservations pour les propriétaires, restaurants et salons. | Base de données Django & Python |
| **Lutte contre le No-Show** | Mise en place de mécanismes basés sur la traçabilité pour réduire l'absentéisme dans les services. | HCS et Logique Métier Sécurisée |


-----

## ⚙️ Project Setup (Local Installation) 🚀

Cette section guide l'utilisateur à travers les étapes nécessaires pour cloner, configurer et exécuter EsikaGo localement.

### 🧩 Prérequis

Assurez-vous que les logiciels suivants sont installés et configurés sur votre système :

  * **Python 3.9+** : Requis pour exécuter le backend Django.
  * **pip** et **virtualenv** : Pour la gestion des paquets et l'isolation de l'environnement Python.
  * **Java SDK (JDK)** : **Essentiel** pour les dépendances de communication Hedera (gRPC). Le JDK doit être installé et son répertoire de binaires (`bin`) ajouté à la variable d'environnement système **`PATH`**.
  * **Git** : Pour cloner le dépôt du projet.

-----

### 🪄 Étapes d’installation

Suivez ces étapes pour installer et initialiser l'application :

#### 1\. Cloner le Projet

Ouvrez votre terminal ou invite de commande et clonez le dépôt :

```bash
git clone https://github.com/Tharzan/esikaGo.git
cd esikaGo
```

#### 2\. Créer et Activer l'Environnement Virtuel

Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet :

```bash
python -m venv venv
# Sous Linux/Mac OS:
source venv/bin/activate
# Sous Windows:
venv\Scripts\activate
```

#### 3\. Installer les Dépendances Python

Une fois l'environnement activé, installez toutes les bibliothèques nécessaires, y compris Django, DeepFace, et les SDK Hedera :

```bash
pip install -r requirements.txt
```

#### 4\. Initialiser la Base de Données

Le projet utilise **SQLite** (`db.sqlite3`). La base de données est fournie avec des données de test initiales. Vous devez cependant exécuter les commandes de migration pour vous assurer que le schéma est à jour :

```bash
python manage.py makemigrations
python manage.py migrate
```

-----

## 🔑 Utilisation et Données de Test Rapides

Pour tester rapidement les fonctionnalités Hedera et la signature numérique, vous pouvez utiliser un compte de test préconfiguré.

### Informations de Connexion

| Rôle | Mot de Passe | Numéro de Téléphone |
| :--- | :--- | :--- |
| **Utilisateur de Test** | `tharcisse` | `0813316463` |

### Scénario de Test

1.  Connectez-vous avec les informations ci-dessus.
2.  Naviguez vers le tableau de bord, puis **Gestion et Bien Immobilier**. Vous pourrez y enregistrer le paiement d'un loyer.
3.  Lors de l'enregistrement, vous verrez un reçu généré, **ancré sur Hedera** et portant votre **signature numérique**.

> **⚠️ ATTENTION : Configuration de Sécurité**
>
> Avant de pouvoir signer un document, vous devez d'abord configurer vos informations de sécurité :
>
>   * Un **nouveau mot de passe** sera demandé pour chiffrer la clé privée.
>   * Une **image de référence** sera requise pour la reconnaissance faciale (utilisée pour l'authentification lors de la signature).
## la premiere fois le processus sera long en fonction de votre conneion car dois telecharger un fichjier de plus de 500M pour la verification faciale

### Navigation Additionnelle

  * Pour explorer la partie **Gestion Commerciale** (restaurants, salons de beauté), cliquez sur le menu en forme de tableau (ou **Gestion** dans la barre latérale) et choisissez le module un Restaurant.

-----

6. Lancer le serveur
Démarrez l'application web Django :

Bash

python manage.py runserver
L’application sera accessible sur : 👉 http://127.0.0.1:8000/

☁️ Configuration Hedera et Variables d'Environnement
Le projet nécessite vos identifiants Hedera (pour l'ancrage des reçus) et d'autres paramètres sensibles. Ces informations doivent être stockées dans un fichier de variables d'environnement (.env) qui ne sera pas partagé publiquement.

Étapes de Configuration
Renommer le fichier d'exemple : Un fichier d'exemple nommé .env.example est fourni à la racine du projet. Renommez-le en .env :

Bash

cp .env.example .env
Renseigner les informations : Ouvrez le fichier nouvellement créé .env et remplacez les valeurs de substitution par vos propres identifiants du réseau Hedera (Testnet ou Mainnet).

Le fichier doit contenir (au minimum) les variables suivantes :

Extrait de code

# Identifiants de votre compte Opérateur Hedera
HEDERA_ACCOUNT_ID=0.0.xxxx
HEDERA_PRIVATE_KEY="302e020100300706052b8104000a04220420..." 
HCS_TOPIC_ID_STRING = "0.0.xxxxxxx" remplacer 
# Réseau utilisé : 'testnet' ou 'mainnet'
HEDERA_NETWORK=testnet


6. **Lancer le serveur**
   ```bash
   python manage.py runserver
   ```

   L’application sera accessible sur :  
   👉 http://127.0.0.1:8000/

---

###Compris, Tharcisse. Je vais simplifier votre guide d'installation du JDK pour le rendre plus direct et facile à suivre dans votre `README`. J'inclus un lien direct et j'épure les étapes.

-----

## 7\. ☕ Configuration du Java Development Kit (JDK)

Le SDK Hedera utilisé par votre projet Python nécessite le **JDK** pour sa couche de communication (gRPC). **Le JRE standard ne suffit pas.**

### Étape 1 : Téléchargement et Installation du JDK

Téléchargez et installez une version récente du JDK (comme la version 17 ou plus).

  * **Lien Recommandé (Oracle) :** [https://www.oracle.com/java/technologies/downloads/](https://www.oracle.com/java/technologies/downloads/)
  * **Action :** Exécutez le programme d'installation. **Notez le chemin d'installation** (par exemple, `C:\Program Files\Java\jdk-17.0.x`).

### Étape 2 : Configuration des Variables d'Environnement

Vous devez définir la variable **`JAVA_HOME`** et ajouter le dossier `bin` du JDK au **`PATH`**.

#### 🖥️ Windows

1.  Recherchez et ouvrez **"Modifier les variables d'environnement système"**.
2.  Cliquez sur **Variables d'environnement...**.
3.  **Créer `JAVA_HOME` :** Sous **Variables système**, cliquez sur **Nouvelle** :
      * **Nom :** `JAVA_HOME`
      * **Valeur :** Collez le chemin de votre dossier JDK (Ex: `C:\Program Files\Java\jdk-17.0.x`). **N'incluez pas le dossier `bin` \!**
4.  **Modifier `PATH` :** Dans la liste des **Variables système**, sélectionnez **`Path`** et ajoutez une nouvelle entrée :
      * `%JAVA_HOME%\bin`
5.  Validez et fermez toutes les fenêtres.

#### 🐧 macOS / Linux

1.  Ouvrez votre fichier de configuration de shell (`~/.zshrc` ou `~/.bashrc`) avec un éditeur.

2.  Ajoutez ces lignes, en remplaçant le chemin si vous n'utilisez pas l'installation par défaut :

    ```bash
    # Définir la variable JAVA_HOME
    export JAVA_HOME="/chemin/vers/votre/jdk" 

    # Ajouter le dossier bin du JDK au PATH
    export PATH="$JAVA_HOME/bin:$PATH" 
    ```

3.  Enregistrez, fermez l'éditeur, puis exécutez `source ~/.votre_fichier_shell` pour appliquer les changements immédiatement.

### Étape 3 : Vérification

Ouvrez une **nouvelle** fenêtre de terminal et vérifiez que tout est correct :

```bash
# Vérifie si Java est accessible
java -version

# Vérifie le chemin de la variable JAVA_HOME
echo $JAVA_HOME
```

Si ces commandes affichent les bonnes informations, vous pouvez passer à l'étape suivante de l'installation du projet.


## 🧱 Architecture Diagram

```
[Frontend/UI] --> [Django Backend] --> [Hedera SDK Python/Java]
                                     ↳ [Hedera Network (Testnet)]
                                     ↳ [Mirror Node Explorer]
```

---

## 🧩 Hedera Integration Summary

| Service | Utilisation | Justification |
|----------|--------------|----------------|
| **HCS (Consensus Service)** | Enregistrement immuable des contrats et paiements | Coût fixe bas ($0.0001) et auditabilité garantie |
| **HTS (Token Service)** | Tokenisation des actifs immobiliers | Simplifie la gestion de propriété fractionnée |
| **HSCS (Smart Contracts)** | Validation automatique des loyers et transferts | Permet des flux transparents sans intermédiaire |
| **DID (Identity)** | Vérification d’identité du locataire/propriétaire | Renforce la confiance et la conformité légale |

---

## 🧪 Tests & Vérification


Pour vérifier une transaction sur le **Hedera Mirror Node Explorer**, utilisez le hash retourné après chaque interaction blockchain :
👉 [https://hashscan.io/testnet](https://hashscan.io/testnet)



## ⚠️ Note sur l'Intégration et l'État Actuel du Projet

Ce projet a été  en cours de développé mais apres la prise de connaissance du Hackathon Hedera, dans une course contre la montre. j'ai entamé le développement à peine **dix jours** avant la date limite de soumission.

### ⏳ Contraintes et Objectifs Réalisés

1.  **Objectif Principal atteint : Soumission dans les délais.** Malgré les contraintes de temps, notre priorité était de soumettre une preuve de concept fonctionnelle.
2.  **Intégration Hedera :** Le réseau Hedera représente une solution fondamentale pour résoudre le manque de traçabilité et de confiance en Afrique. Bien que l'ambition soit d'utiliser le plein potentiel des services Hedera, nous avons concentré nos efforts sur l'intégration du **Hedera Consensus Service (HCS)** pour l'ancrage des documents, en raison des délais serrés.

### ✨ Potentiel Futur et Vision (Roadmap)

Le potentiel du projet EsikaGo est bien plus large que la version soumise. Notre *pitch deck* fournit un aperçu détaillé des fonctionnalités futures que nous souhaitons implémenter en utilisant :

* **Hedera Token Service (HTS) :** Pour la tokenisation des actifs (propriétés).
* **Hedera Smart Contract Service (HSCS) :** Pour l'automatisation de la gestion locative.
* **Identités Décentralisées (DID) :** Pour une authentification utilisateur et documentaire renforcée.

### 🤝 Notre Attente du Programme Hedera

L'objectif de cette soumission est de démontrer la vision et la faisabilité d'EsikaGo. Pour passer à l'étape suivante, nous recherchons :

1.  **Mentorats Techniques :** Un accompagnement par des experts Hedera pour nous aider à exploiter l'intégralité du SDK et finaliser l'architecture *Web3*.
2.  **Financement :** Des ressources financières pour mobiliser une équipe de développement à temps plein, résoudre les aspects restants du projet, et produire des démonstrations et du contenu vidéo de niveau professionnel.

Nous nous excusons pour le caractère non-professionnel de la vidéo youtube de soumission. Mon budget actuel et  concentration sur le code m'ont empêchés d'embaucher une équipe de production. Notre engagement principal reste la qualité et la finalisation du produit.

---

## Team EsikaGo
Nkongolo Mukoma Tharcisse — Chef de projet & Développeur principal

📧 tharcissenkongolo02@gmail.com

💡 Spécialités : Data Science, Machine Learning (ML), Développement Front-end & Back-end.

---

## 🧾 Licence

© 2025 EsikaGo - Tous droits réservés.  
Projet développé dans le cadre du **Hedera Africa Hackathon 2025**.

