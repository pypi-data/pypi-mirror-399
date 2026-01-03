# 📦 CLI Package - RGPD_PRO Client

Ce dossier contient tout ce qu'il faut pour publier le CLI client sur PyPI.

## 📁 Contenu

```
cli_package/
├── cli_remote.py              # CLI client (point d'entrée)
├── setup.py                   # Configuration setuptools
├── pyproject.toml             # Configuration moderne Python
├── MANIFEST.in                # Contrôle des fichiers inclus
├── README_CLIENT.md           # Documentation utilisateur
├── requirements_client.txt    # Dépendances (requests)
└── build_publish.py           # Script de build/publish
```

## 🚀 Comment publier

### 1. Prérequis

```bash
pip install build twine
```

### 2. Créer un compte PyPI

https://pypi.org/account/register/

### 3. Builder et publier

```bash
cd cli_package
python build_publish.py
```

Choisis :
- Option 6 : Full workflow (clean → build → test)
- Option 5 : Upload to PyPI (après avoir testé)

## 🧪 Tester localement

```bash
cd cli_package
python build_publish.py  # Option 6
rgpd-scan  # Teste le CLI
```

## 📝 Modifier la version

Édite dans `setup.py` et `pyproject.toml` :
```python
version="2.0.1"  # Incrémente la version
```

## 🌐 Changer l'URL du serveur

Édite `cli_remote.py` ligne 95 :
```python
default_url = "http://ton-domaine.com"
```

## ✅ Après publication

Les utilisateurs pourront installer :
```bash
pip install rgpd-pro-client
rgpd-scan
```
