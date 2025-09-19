#!/usr/bin/env python3
"""
Script pour construire TorrentHunt Desktop avec Top 100
Fonctionnalités: Recherche + Top 100 par catégories (Audio, Video, Books, etc.)
"""

import subprocess
import sys
import os

def build_top100():
    """Construire la version avec Top 100"""

    print("📈 Construction de TorrentHunt Desktop avec TOP 100")
    print("=" * 70)
    print("🆕 NOUVELLES FONCTIONNALITÉS:")
    print("   🔍 Onglet Recherche classique")
    print("   📈 Onglet Top 100 par catégories")
    print("   🎵 Catégories: Audio, Video, TV, Books, Games, Software, Anime")
    print("   📊 Tri des colonnes")
    print("   ☑️ Sélection des sites")
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
        "--name=TorrentHunt_Desktop_TOP100",
        "--hidden-import=aiohttp",
        "--hidden-import=tkinter",
        "--hidden-import=asyncio",
        "--clean",
        "desktop_torrent_search_top100.py"
    ]

    try:
        subprocess.check_call(cmd)
        print("🎉 BUILD TOP 100 RÉUSSI!")

        exe_path = "dist/TorrentHunt_Desktop_TOP100"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 Fichier: {exe_path}")
            print(f"📏 Taille: {size_mb:.1f} MB")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if build_top100():
        print("\n" + "="*70)
        print("🎉 TORRENTHUNT DESKTOP TOP 100 PRÊT !")
        print("")
        print("🆕 FONCTIONNALITÉS COMPLÈTES:")
        print("📑 ONGLET RECHERCHE:")
        print("   🔍 Recherche par mots-clés")
        print("   📊 Tri des colonnes (nom, taille, seeders, etc.)")
        print("   ☑️ Sélection des sites torrent")
        print("   🎯 Recherche multi-sites en parallèle")
        print("")
        print("📈 ONGLET TOP 100:")
        print("   🌟 Tous - Top général")
        print("   🎵 Audio/Musique - Albums, MP3, FLAC")
        print("   🎬 Vidéo/Films - Movies, MP4, MKV")
        print("   📺 Séries TV - Episodes, Seasons")
        print("   📚 Livres/eBooks - PDF, EPUB")
        print("   🎮 Jeux - PC, Console Games")
        print("   💻 Logiciels - Apps, Programs")
        print("   🎌 Anime - Japanese Animation")
        print("")
        print("⚡ PERFORMANCE:")
        print("   ✅ Sessions HTTP fraîches (bug recherches multiples corrigé)")
        print("   ✅ Interface avec onglets")
        print("   ✅ Tri intelligent par colonne")
        print("   ✅ Filtrage par catégorie automatique")
        print("")
        print("📁 Executable: dist/TorrentHunt_Desktop_TOP100")
        print("🌐 API: https://torrent-api-py-nx0x.onrender.com")
        print("🔗 Endpoints: /api/v1/search + /api/v1/trending")
        print("="*70)
    else:
        sys.exit(1)