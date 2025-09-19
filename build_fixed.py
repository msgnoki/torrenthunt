#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop FIXED
🐛 Bug recherches multiples corrigé
"""

import subprocess
import sys
import os

def build_fixed():
    """Construire la version fixed"""

    print("🐛 Construction de TorrentHunt Desktop FIXED")
    print("=" * 60)
    print("🔧 CORRECTIFS APPLIQUÉS:")
    print("   ✅ Sessions HTTP fraîches pour chaque recherche")
    print("   ✅ Fermeture correcte des connexions aiohttp")
    print("   ✅ Nouvelle boucle asyncio pour chaque recherche")
    print("   ✅ Logs de debug pour diagnostiquer")
    print("   ✅ Plus de bug 'deuxième recherche vide' !")

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
        "--name=TorrentHunt_Desktop_FIXED",
        "--hidden-import=aiohttp",
        "--hidden-import=tkinter",
        "--hidden-import=asyncio",
        "--clean",
        "desktop_torrent_search_fixed.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("🎉 BUILD FIXED RÉUSSI!")

        exe_path = "dist/TorrentHunt_Desktop_FIXED"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Fichier: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if build_fixed():
        print("\n" + "="*60)
        print("🎉 TORRENTHUNT DESKTOP FIXED PRÊT !")
        print("")
        print("🐛 BUG CORRIGÉ:")
        print("❌ Avant: Deuxième recherche = 0 résultat")
        print("✅ Maintenant: Recherches multiples fonctionnelles !")
        print("")
        print("📋 TESTS À FAIRE:")
        print("1. Première recherche → résultats OK")
        print("2. Deuxième recherche → résultats OK aussi !")
        print("3. Troisième recherche → toujours OK")
        print("4. Changer de sites → OK")
        print("5. Trier colonnes → OK")
        print("")
        print("📁 Executable: dist/TorrentHunt_Desktop_FIXED")
        print("🌐 API: https://torrent-api-py-nx0x.onrender.com")
        print("="*60)
    else:
        sys.exit(1)