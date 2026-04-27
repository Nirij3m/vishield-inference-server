# ViShield — Backend

Serveur d'inférence Python / FastAPI pour la détection de hameçonnage en temps réel. Il reçoit les enregistrements d'appels transmis, effectue la transcription vocale via Vosk, puis analyse le texte avec un modèle de classification.

---

## Prérequis

- Python 3.10 ou supérieur
- `pip` installé
- `ffmpeg` installé sur le système
- Le dépôt cloné en local (voir étape 1)
- Le modèle Vosk téléchargé (voir étape 2)

---

## Étape 1 — Récupérer le projet

Clonez le dépôt GitHub sur votre machine :

```bash
git clone https://github.com/Nirij3m/vishield-inference-server
cd vishield-inference-server
```

---

## Étape 2 — Télécharger le modèle de transcription

Le serveur utilise **Vosk** pour la transcription audio (Speech-to-Text). Téléchargez le modèle `vosk-model-en-us-0.22` depuis la page officielle :

```
https://alphacephei.com/vosk/models
```

Une fois téléchargé, dézippez l'archive directement dans le répertoire du projet :

```
vishield-inference-server/
├── api.py
├── requirements.txt
├── vosk-model-en-us-0.22/   <-- dossier extrait ici
└── ...
```

**Vérification :** le dossier `vosk-model-en-us-0.22` doit se trouver à la racine du projet et contenir les fichiers du modèle (notamment `am/`, `conf/`, `graph/`).

---

## Étape 3 — Installer ffmpeg

`ffmpeg` est un outil système requis pour le traitement des fichiers audio. Il doit être installé séparément de Python.

### Windows

La méthode recommandée est d'utiliser le gestionnaire de paquets **Chocolatey** :

```bash
choco install ffmpeg
```

Si Chocolatey n'est pas installé sur votre machine, consultez : https://chocolatey.org/install

Alternativement, téléchargez les binaires manuellement depuis https://ffmpeg.org/download.html et ajoutez le dossier `bin/` à la variable d'environnement `PATH`.

### Linux (Debian / Ubuntu)

```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

**Vérification :** dans un nouveau terminal, exécutez :

```bash
ffmpeg -version
```

La sortie doit commencer par une ligne du type `ffmpeg version X.X.X`.

---

## Étape 4 — Installer les dépendances

Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.

### Créer et activer l'environnement virtuel

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Installer les paquets

Utilisez le binaire `pip` de l'environnement virtuel pour vous assurer que les dépendances sont installées dans le bon environnement :

**Windows**

```bash
venv\Scripts\pip install -r requirements.txt
```

**Linux / macOS**

```bash
venv/bin/pip install -r requirements.txt
```

Le fichier `requirements.txt` contient notamment :

```
fastapi
torch
transformers
pandas
python-multipart
uvicorn
pydantic
vosk
ffmpeg-python
python-dotenv
```

**Vérification :** assurez-vous qu'aucune erreur n'apparaît pendant l'installation. En cas d'erreur sur `torch`, consultez https://pytorch.org/get-started/locally/ pour installer la version adaptée à votre système.

---

## Étape 5 — Configurer les variables d'environnement (optionnel)

Le serveur utilise `python-dotenv` pour charger les variables d'environnement depuis un fichier `.env` à la racine du projet. Ce fichier n'est pas versionné et doit être créé manuellement.

### HF_TOKEN

`HF_TOKEN` est le token d'accès à l'API Hugging Face. Il est utilisé au démarrage du serveur pour télécharger le modèle de classification `Nirij3m/roberta-finetuned-vishing` depuis le Hub. Sa présence est optionnelle mais peut accélérer le téléchargement du modèle.

```python
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, token=access_token)
tokenizer = AutoTokenizer.from_pretrained(checkpoint, token=access_token)
```

Si la variable est absente, le serveur démarre tout de même mais affiche un avertissement et tente de charger le modèle sans authentification :

```
UserWarning: HF_TOKEN not found in environment variables
```

### Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet :

```
vishield-inference-server/
├── api.py
├── .env        <-- à créer ici
└── ...
```

Contenu du fichier :

```
HF_TOKEN=your_token_here
```

Remplacez `your_token_here` par votre token Hugging Face. Pour obtenir un token :

1. Connectez-vous sur https://huggingface.co
2. Allez dans **Settings > Access Tokens**
3. Créez un token avec le rôle **Read**
4. Copiez la valeur générée dans le fichier `.env`

---

## Étape 6 — Lancer le serveur

### Windows

```bash
python.exe -m uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

### Linux / macOS

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

En cas de succès, le terminal affiche :

```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

> L'option `--reload` redémarre automatiquement le serveur à chaque modification du code. Retirez-la en environnement de production.

---

## Étape 6 — Renseigner l'adresse IP dans l'application Android

L'application ViShield doit connaître l'adresse IP de la machine hébergeant le serveur ainsi que le port (`8080`).

### Obtenir l'adresse IP locale de votre machine

**Windows**

```bash
ipconfig
```

Repérez la ligne **Adresse IPv4** dans la section correspondant à votre interface réseau active (Wi-Fi ou Ethernet).

**Linux / macOS**

```bash
ip a
```

Repérez l'adresse sous l'interface active (ex. `eth0` ou `wlan0`), sur la ligne préfixée par `inet`.

L'adresse ressemble à :

```
192.168.X.XXX
```

### Renseigner dans l'application

Dans l'application **ViShield**, saisissez l'adresse IP et le port du serveur au premier démarrage de l'application ou dans l'onglet **Settings > Server Configuration**
> Le téléphone et l'ordinateur doivent être connectés au même réseau Wi-Fi.

---

## Résolution des problèmes courants

| Problème | Solution |
|---|---|
| `ModuleNotFoundError` au démarrage | Vérifiez que l'environnement virtuel est activé et que `pip install -r requirements.txt` a été exécuté |
| `FileNotFoundError` sur le modèle Vosk | Vérifiez que le dossier `vosk-model-en-us-0.22` est bien à la racine du projet |
| Erreur sur `torch` à l'installation | Installez manuellement la version adaptée à votre système depuis https://pytorch.org/get-started/locally/ |
| `Address already in use` au démarrage | Le port 8080 est déjà occupé — arrêtez le processus existant ou changez le port avec `--port 8081` |
| L'application Android ne contacte pas le serveur | Vérifiez que le téléphone et l'ordinateur sont sur le même réseau Wi-Fi et que le pare-feu autorise le port 8080 |
| `ffmpeg` introuvable | Installez ffmpeg : `choco install ffmpeg` (Windows) ou `sudo apt install ffmpeg` (Linux) |

---

## Structure du projet

```
vishield-inference-server/
├── api.py
├── requirements.txt
├── .env
├── vosk-model-en-us-0.22/
│   ├── am/
│   ├── conf/
│   ├── graph/
│   └── ...
└── README.md
```
