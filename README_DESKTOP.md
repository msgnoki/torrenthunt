# TorrentHunt Desktop

Application desktop pour rechercher des torrents, basée sur le bot Telegram TorrentHunt.

## 🚀 Fonctionnalités

- **Interface graphique intuitive** avec Tkinter
- **Recherche multi-sites** : 1337x, ThePirateBay, TorrentGalaxy, RARBG, Nyaa, YTS, EZTV
- **Résultats détaillés** : nom, taille, seeders, leechers, uploader
- **Actions rapides** :
  - Copier le lien magnet
  - Ouvrir dans le navigateur
  - Lancer le client torrent par défaut
- **Interface responsive** avec barre de progression

## 📦 Installation

### Option 1: Exécuter directement le script Python

```bash
# Installer les dépendances
pip install aiohttp py1337x loguru

# Lancer l'application
python desktop_torrent_search.py
```

### Option 2: Créer un exécutable standalone

```bash
# Lancer le script de construction
python build_executable.py
```

L'exécutable sera créé dans le dossier `dist/` et peut être distribué sans installer Python.

## 🖥️ Utilisation

1. **Lancer l'application**
2. **Choisir un site** de torrent dans la liste déroulante
3. **Entrer votre recherche** dans le champ de texte
4. **Cliquer sur "Rechercher"** ou appuyer sur Entrée
5. **Interagir avec les résultats** :
   - Double-clic pour copier le lien magnet
   - Clic droit pour le menu contextuel
   - Actions disponibles: copier magnet, ouvrir dans navigateur, télécharger

## 🔧 Configuration

### Sites supportés

- **1337x** : Recherche complète avec API intégrée
- **Autres sites** : Recherche simulée (à implémenter selon besoins)

### Personnalisation

Modifiez le fichier `desktop_torrent_search.py` pour :
- Ajouter de nouveaux sites
- Personnaliser l'interface
- Modifier les actions disponibles

## 📁 Structure des fichiers

```
TorrentHunt/
├── desktop_torrent_search.py    # Application principale
├── build_executable.py          # Script de construction
├── README_DESKTOP.md            # Cette documentation
└── dist/                        # Exécutables générés
    └── TorrentHunt_Desktop      # Exécutable final
```

## 🛠️ Développement

### Dépendances

- `tkinter` : Interface graphique (inclus avec Python)
- `aiohttp` : Requêtes HTTP async
- `py1337x` : API pour 1337x
- `asyncio` : Programmation asynchrone
- `threading` : Exécution en arrière-plan

### Construction d'exécutable

Le script `build_executable.py` utilise PyInstaller pour créer un exécutable standalone :

- **--onefile** : Un seul fichier exécutable
- **--windowed** : Pas de console
- **--clean** : Nettoyage avant construction
- **Optimisations** : Exclusion de modules non nécessaires

## 🚨 Avertissements

- **Usage légal uniquement** : Respectez les lois de votre pays
- **Contenu sous copyright** : Ne téléchargez que du contenu libre de droits
- **Sécurité** : Vérifiez toujours les fichiers téléchargés

## 🐛 Résolution de problèmes

### L'application ne se lance pas
- Vérifiez que Python 3.8+ est installé
- Installez les dépendances manquantes
- Vérifiez les permissions d'exécution

### Pas de résultats de recherche
- Vérifiez votre connexion internet
- Les sites peuvent être temporairement indisponibles
- Essayez un autre site de torrent

### Erreur lors de la construction d'exécutable
- Assurez-vous que PyInstaller est installé
- Libérez de l'espace disque
- Fermez les antivirus temporairement

## 📞 Support

Pour des problèmes ou suggestions :
1. Vérifiez les problèmes connus ci-dessus
2. Consultez les logs dans la console
3. Créez une issue dans le repository principal

## 📜 Licence

Basé sur le projet TorrentHunt original. Utilisez de manière responsable et légale.