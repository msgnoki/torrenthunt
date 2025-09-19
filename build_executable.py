#!/usr/bin/env python3
"""
Script pour créer un exécutable desktop de TorrentHunt
Utilise PyInstaller pour créer un fichier .exe/.app standalone
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Vérifier si PyInstaller est installé"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Installer PyInstaller"""
    print("Installation de PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print("✗ Erreur lors de l'installation de PyInstaller")
        return False


def create_requirements_desktop():
    """Créer un fichier requirements pour la version desktop"""
    requirements = [
        "aiohttp==3.11.9",
        "1337x==2.0.1",
        "py1337x",
        "loguru==0.7.2"
    ]

    with open("requirements_desktop.txt", "w") as f:
        f.write("\n".join(requirements))

    print("✓ Fichier requirements_desktop.txt créé")


def build_executable():
    """Construire l'exécutable avec PyInstaller"""
    script_name = "desktop_torrent_search.py"

    if not os.path.exists(script_name):
        print(f"✗ Fichier {script_name} non trouvé")
        return False

    print("Construction de l'exécutable...")

    # Options PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Un seul fichier exécutable
        "--windowed",                   # Pas de console (pour GUI)
        "--name=TorrentHunt_Desktop",   # Nom de l'exécutable
        "--icon=icon.ico",              # Icône (optionnel)
        "--add-data=*;.",               # Inclure les données
        "--hidden-import=py1337x",      # Modules cachés
        "--hidden-import=aiohttp",
        "--hidden-import=tkinter",
        "--clean",                      # Nettoyer avant construction
        script_name
    ]

    # Retirer l'icône si elle n'existe pas
    if not os.path.exists("icon.ico"):
        cmd = [c for c in cmd if not c.startswith("--icon")]

    try:
        subprocess.check_call(cmd)
        print("✓ Exécutable créé avec succès")

        # Localiser l'exécutable
        dist_path = Path("dist")
        if dist_path.exists():
            executable_files = list(dist_path.glob("TorrentHunt_Desktop*"))
            if executable_files:
                exe_path = executable_files[0]
                print(f"✓ Exécutable disponible: {exe_path}")
                print(f"  Taille: {exe_path.stat().st_size / (1024*1024):.1f} MB")
                return True

        print("✗ Exécutable non trouvé dans le dossier dist/")
        return False

    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur lors de la construction: {e}")
        return False


def create_spec_file():
    """Créer un fichier .spec personnalisé pour plus de contrôle"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_torrent_search.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['py1337x', 'aiohttp', 'tkinter', 'asyncio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest', 'matplotlib', 'numpy', 'pandas', 'scipy',
        'PIL', 'cv2', 'torch', 'tensorflow'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TorrentHunt_Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    with open("torrenthunt_desktop.spec", "w") as f:
        f.write(spec_content.strip())

    print("✓ Fichier .spec créé")


def clean_build_files():
    """Nettoyer les fichiers de construction"""
    dirs_to_clean = ["build", "__pycache__"]
    files_to_clean = ["*.spec"]

    for dirname in dirs_to_clean:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            print(f"✓ Dossier {dirname} supprimé")

    import glob
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"✓ Fichier {file} supprimé")


def main():
    """Point d'entrée principal"""
    print("🔧 Construction de TorrentHunt Desktop")
    print("=" * 50)

    # Vérifier PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ Impossible d'installer PyInstaller")
            return 1

    # Créer les fichiers nécessaires
    create_requirements_desktop()

    # Option: utiliser un fichier .spec personnalisé
    use_spec = input("Utiliser un fichier .spec personnalisé? (y/N): ").lower().startswith('y')

    if use_spec:
        create_spec_file()
        # Construire avec le fichier .spec
        try:
            subprocess.check_call(["pyinstaller", "torrenthunt_desktop.spec"])
            print("✓ Construction terminée avec fichier .spec")
        except subprocess.CalledProcessError:
            print("✗ Erreur avec le fichier .spec")
            return 1
    else:
        # Construction standard
        if not build_executable():
            return 1

    # Instructions finales
    print("\n" + "=" * 50)
    print("🎉 Construction terminée!")
    print("\nInstructions:")
    print("1. L'exécutable se trouve dans le dossier 'dist/'")
    print("2. Vous pouvez le distribuer sans installer Python")
    print("3. Double-cliquez pour lancer l'application")

    # Nettoyer si demandé
    clean = input("\nNettoyer les fichiers de construction? (Y/n): ")
    if not clean.lower().startswith('n'):
        clean_build_files()

    return 0


if __name__ == "__main__":
    sys.exit(main())