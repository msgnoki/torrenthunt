#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop v2 avec recherches réelles
"""

import subprocess
import sys
import os

def build_executable_v2():
    """Construire la nouvelle version avec PyInstaller"""

    print("🔧 Construction de TorrentHunt Desktop v2")
    print("=" * 50)

    # Installer les dépendances
    print("📦 Installation des dépendances...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_desktop_v2.txt"])

    # Nettoyer les anciens builds
    import shutil
    for dir_name in ["build", "dist", "__pycache__"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Nettoyage: {dir_name} supprimé")

    # Construire avec PyInstaller
    print("🏗️ Construction de l'exécutable...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=TorrentHunt_Desktop_v2",
        "--hidden-import=py1337x",
        "--hidden-import=aiohttp",
        "--hidden-import=bs4",
        "--hidden-import=lxml",
        "--hidden-import=tkinter",
        "--clean",
        "desktop_torrent_search_v2.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("✅ Exécutable créé avec succès!")

        # Vérifier le fichier créé
        exe_path = "dist/TorrentHunt_Desktop_v2"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Exécutable: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Exécutable non trouvé")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la construction: {e}")
        return False

if __name__ == "__main__":
    success = build_executable_v2()
    if success:
        print("\n🎉 Construction terminée!")
        print("L'exécutable se trouve dans dist/TorrentHunt_Desktop_v2")
    else:
        print("\n💥 Échec de la construction")
        sys.exit(1)