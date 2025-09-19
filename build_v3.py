#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop v3 avec debug mode
"""

import subprocess
import sys
import os

def build_v3():
    """Construire la version v3 avec mode debug"""

    print("🔧 Construction de TorrentHunt Desktop v3 (Debug Mode)")
    print("=" * 60)

    # Nettoyer
    import shutil
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Nettoyage: {dir_name}")

    # Construire
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=TorrentHunt_Desktop_v3",
        "--hidden-import=aiohttp",
        "--hidden-import=bs4",
        "--hidden-import=lxml",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.scrolledtext",
        "--clean",
        "desktop_torrent_search_v3.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("✅ Build réussi!")

        exe_path = "dist/TorrentHunt_Desktop_v3"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Fichier: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if build_v3():
        print("\n🎉 Version v3 prête avec mode debug!")
    else:
        sys.exit(1)