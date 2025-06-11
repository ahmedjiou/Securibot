# Securibot

Securibot est un chatbot spécialisé en cybersécurité conçu pour fournir aux utilisateurs des informations et des conseils sur des sujets courants de cybersécurité. Il propose une authentification des utilisateurs, une interface conversationnelle avec historique, et la capacité de répondre à des questions en cybersécurité.

## Fonctionnalités

- **Page d’accueil :** Une page d'accueil avec des éléments personnalisés.
- **Authentification :** Authentification sécurisée des utilisateurs avec plusieurs options :
  - Mode invité
  - Inscription et connexion par email/mot de passe
  - Authentification via Google
- **Interface de chat :** Une page principale de discussion avec :
  - Un historique déroulant des conversations passées dans une barre latérale
  - Une zone de saisie pour poser des questions liées à la cybersécurité
- **Profil et paramètres :** Pages permettant aux utilisateurs de gérer leur profil et les paramètres de l'application
- **Questions/Réponses en cybersécurité :** Fonctionnalité principale permettant de répondre aux questions des utilisateurs sur la cybersécurité

## Pile technologique

- **Frontend :**
  - Next.js
  - React
  - TypeScript
  - Tailwind CSS (avec les composants shadcn/ui)
  - Radix UI
- **Backend :**

Le backend de Securibot est conçu avec **Python** et **Flask**, et intègre des fonctionnalités avancées pour le traitement des conversations et l'intégration d'une logique RAG (Recherche Augmentée par Génération).

- ***Structure du backend***

- `backend_api/` :
  - `main.py` : point d'entrée principal de l’API Flask.
  - `blueprints/` : contient des modules (blueprints) pour gérer les différentes routes API :
    - `convo_bp.py` : gestion des conversations
    - `fetch_full_convo.py` : récupération complète d'une conversation
    - `fetch_history.py` : historique des conversations
    - `update_history.py` : mise à jour de l'historique
    - `prompt_generation.py` : génération de prompts personnalisés

- `RAG_factory/` :
  - `rag.py` : logique de traitement pour l’implémentation RAG.
  - `cnil_guide_securite_personnelle.pdf` : document de référence CNIL sur la sécurité personnelle.


## Structure du projet

Le projet suit la structure standard d’une application Next.js. Répertoires clés :

- `/src/app` : Contient les pages principales de l’application (ex. : `auth`, `chat`, `profile`, `settings`)
- `/src/components` : Composants React réutilisables (ex. : `chat/ChatMessage`, `ui/...`)
- `/src/lib` : Fonctions utilitaires et interactions avec les API (ex. : `chatApi.ts`, `firebaseAuth.ts`, `types.ts`, `utils.ts`)
- `/src/ai` : Configuration Genkit et définitions des flux d’IA
- `/public` : Ressources statiques
- `/docs` : Documentation du projet (ex. : `/docs/blueprint.md`)

## Démarrage rapide

### Prérequis

- Node.js ainsi que npm ou yarn installés
- Projet Firebase configuré avec l’authentification activée
- Environnement Genkit configuré
- Spline pour l'import d'un élément visuel sur la page de garde

### Lancement du frontend

- Ouvrir Terminal dans le dossier frontend et lancer les commandes suivantes : 
- npm install
- npm run dev
- Ouvrir ensuite le navigateur web à l'adresse spécifiée

### Prérequis

- Python 3.10+
- `pip` ou `poetry` pour la gestion des dépendances
- pip install Flask firebase-admin flask-cors requests python-dotenv sentence-transformers fpdf pinecone-client

### Lancement du backend

- Aller dans le dossier backend :
- Lancer main.py
