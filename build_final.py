#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop Final - Version qui fonctionne !
"""

import subprocess
import sys
import os

def build_final():
    """Construire la version finale qui fonctionne"""

    print("🏴‍☠️ Construction de TorrentHunt Desktop FINAL")
    print("=" * 60)
    print("🎯 Utilise l'API TorrentHunt officielle qui fonctionne !")

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
        "--name=TorrentHunt_Desktop_FINAL",
        "--hidden-import=aiohttp",
        "--hidden-import=tkinter",
        "--hidden-import=asyncio",
        "--clean",
        "desktop_torrent_search_final.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("🎉 BUILD RÉUSSI!")

        exe_path = "dist/TorrentHunt_Desktop_FINAL"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Fichier: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            print(f"🌐 API: https://torrent-api-py-nx0x.onrender.com")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if build_final():
        print("\n" + "="*60)
        print("🎉 VERSION FINALE PRÊTE !")
        print("✅ Cette version utilise l'API TorrentHunt qui fonctionne")
        print("✅ Recherche réelle sur 7 sites: PirateBay, 1337x, etc.")
        print("✅ Vrais noms de torrents, seeders, magnet links")
        print("📁 Executable: dist/TorrentHunt_Desktop_FINAL")
        print("="*60)
    else:
        sys.exit(1)