#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop Enhanced
Fonctionnalités: Tri des colonnes + Sélection de sites
"""

import subprocess
import sys
import os

def build_enhanced():
    """Construire la version enhanced"""

    print("🚀 Construction de TorrentHunt Desktop ENHANCED")
    print("=" * 65)
    print("✨ Nouvelles fonctionnalités:")
    print("   📊 Tri ascendant/descendant des colonnes")
    print("   ☑️ Cases à cocher pour sélectionner les sites")
    print("   🎯 Recherche sur sites sélectionnés uniquement")
    print("   🏴‍☠️ API TorrentHunt officielle")

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
        "--name=TorrentHunt_Desktop_ENHANCED",
        "--hidden-import=aiohttp",
        "--hidden-import=tkinter",
        "--hidden-import=asyncio",
        "--clean",
        "desktop_torrent_search_enhanced.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("🎉 BUILD ENHANCED RÉUSSI!")

        exe_path = "dist/TorrentHunt_Desktop_ENHANCED"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Fichier: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if build_enhanced():
        print("\n" + "="*65)
        print("🎉 TORRENTHUNT DESKTOP ENHANCED PRÊT !")
        print("")
        print("🆕 NOUVELLES FONCTIONNALITÉS:")
        print("📊 Cliquez sur les en-têtes de colonnes pour trier ↕️")
        print("☑️ Sélectionnez/désélectionnez les sites torrent")
        print("🎯 Recherche uniquement sur les sites cochés")
        print("✅ Boutons 'Tout sélectionner' / 'Tout déselectionner'")
        print("📈 Indicateur du nombre de sites sélectionnés")
        print("")
        print("📁 Executable: dist/TorrentHunt_Desktop_ENHANCED")
        print("🌐 API: https://torrent-api-py-nx0x.onrender.com")
        print("="*65)
    else:
        sys.exit(1)