#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop - Modern Interface
Style Flathub avec thème sombre/clair et design épuré
"""

import subprocess
import sys
import os

def build_modern():
    """Construire la version moderne style Flathub"""

    print("🎨 Construction de TorrentHunt Desktop - MODERN INTERFACE")
    print("=" * 75)
    print("✨ DESIGN FLATHUB STYLE:")
    print("   🎨 Interface moderne et épurée")
    print("   🌙 Thèmes sombre/clair interchangeables")
    print("   📱 Layout responsive avec sidebar")
    print("   🎯 UX optimisée pour Linux desktop")
    print("   ⚡ Performance améliorée")
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
        "--name=TorrentHunt_Desktop_MODERN",
        "--hidden-import=aiohttp",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=asyncio",
        "--hidden-import=webbrowser",
        "--clean",
        "desktop_torrent_search_modern.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("🎉 BUILD MODERN RÉUSSI!")

        exe_path = "dist/TorrentHunt_Desktop_MODERN"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Fichier: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if build_modern():
        print("\n" + "="*75)
        print("🎉 TORRENTHUNT DESKTOP MODERN PRÊT !")
        print("")
        print("🎨 INTERFACE MODERNE STYLE FLATHUB:")
        print("")
        print("📱 LAYOUT MODERNE:")
        print("   🏠 Header avec titre et contrôles thème")
        print("   📋 Sidebar de navigation avec sections")
        print("   🔍 Zone de recherche intégrée")
        print("   📂 Sélection de catégories par radio buttons")
        print("   ☑️ Cases à cocher pour sites torrent")
        print("   📊 Table de résultats avec tri avancé")
        print("   📄 Footer avec status et infos API")
        print("")
        print("🌙 THÈMES VISUELS:")
        print("   🌑 Mode sombre (par défaut) - Design moderne")
        print("   ☀️ Mode clair - Interface épurée")
        print("   🎨 Palette de couleurs cohérente")
        print("   ✨ Transitions et hover effects")
        print("")
        print("⚡ FONCTIONNALITÉS:")
        print("   🔍 Recherche multi-sites en parallèle")
        print("   📈 Mode Trending/Popular torrents")
        print("   📂 Filtrage par catégories intelligent")
        print("   📊 Tri par colonnes (nom, taille, seeders)")
        print("   🎯 Indicateurs visuels selon seeders")
        print("   🔗 Ouverture magnet links directe")
        print("")
        print("🐧 OPTIMISÉ POUR LINUX:")
        print("   📦 Prêt pour distribution Flathub")
        print("   🎯 Interface adaptée aux DEs Linux")
        print("   ⚡ Performance optimisée")
        print("   🔧 Gestion moderne des sessions HTTP")
        print("")
        print("📁 Executable: dist/TorrentHunt_Desktop_MODERN")
        print("🌐 API: https://torrent-api-py-nx0x.onrender.com")
        print("🎨 Interface: Modern Flathub Style")
        print("="*75)
    else:
        sys.exit(1)