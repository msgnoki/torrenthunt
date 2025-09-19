#!/usr/bin/env python3
"""
Application desktop pour rechercher des torrents
Utilise les mêmes APIs que le bot Telegram TorrentHunt
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import asyncio
import aiohttp
import threading
import webbrowser
from urllib.parse import quote
import json
from typing import Dict, List, Optional


class TorrentSearchAPI:
    """API client pour rechercher des torrents"""

    def __init__(self):
        self.session = None
        self.base_urls = {
            "1337x": "https://1337x.to",
            "piratebay": "https://thehiddenbay.com",
            "torrentgalaxy": "https://torrentgalaxy.to",
            "rarbg": "https://rargb.to",
            "nyaa": "https://nyaa.si",
            "yts": "https://yts.mx",
            "eztv": "https://eztv.re"
        }

    async def create_session(self):
        """Créer une session HTTP"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )

    async def close_session(self):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def search_1337x(self, query: str, page: int = 1) -> List[Dict]:
        """Recherche sur 1337x"""
        try:
            from py1337x import AsyncPy1337x
            py1337x = AsyncPy1337x()
            results = await py1337x.search(query, page=page)

            torrents = []
            if results and 'items' in results:
                for item in results['items'][:20]:  # Limiter à 20 résultats
                    torrents.append({
                        'name': item.get('name', 'Nom non disponible'),
                        'size': item.get('size', 'Taille inconnue'),
                        'seeders': item.get('seeders', 0),
                        'leechers': item.get('leechers', 0),
                        'uploader': item.get('uploader', 'Inconnu'),
                        'magnet': item.get('magnetLink', ''),
                        'url': item.get('link', ''),
                        'site': '1337x'
                    })
            return torrents
        except Exception as e:
            print(f"Erreur 1337x: {e}")
            return []

    async def search_basic(self, site: str, query: str) -> List[Dict]:
        """Recherche basique avec simulation de résultats"""
        # Simulation de résultats pour les autres sites
        # En production, vous devriez implémenter les vraies APIs
        mock_results = []
        for i in range(5):
            mock_results.append({
                'name': f"{query} - Résultat {i+1} [{site.upper()}]",
                'size': f"{1000 + i*500} MB",
                'seeders': 50 + i*10,
                'leechers': 10 + i*2,
                'uploader': f"User{i+1}",
                'magnet': f"magnet:?xt=urn:btih:{'a'*40}&dn={quote(query)}",
                'url': f"{self.base_urls.get(site, '')}/search/{quote(query)}",
                'site': site
            })
        return mock_results

    async def search(self, query: str, site: str = "1337x", page: int = 1) -> List[Dict]:
        """Rechercher des torrents"""
        await self.create_session()

        try:
            if site == "1337x":
                return await self.search_1337x(query, page)
            else:
                return await self.search_basic(site, query)
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []


class TorrentSearchGUI:
    """Interface graphique pour rechercher des torrents"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TorrentHunt Desktop - Recherche de Torrents")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)

        # Style
        self.setup_styles()

        # API client
        self.api = TorrentSearchAPI()

        # Variables
        self.current_results = []

        # Interface
        self.create_widgets()

        # Configuration de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configuration des styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Couleurs
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

    def create_widgets(self):
        """Créer les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Titre
        title_label = ttk.Label(main_frame, text="🔍 TorrentHunt Desktop", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Frame de recherche
        search_frame = ttk.LabelFrame(main_frame, text="Recherche", padding="10")
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        # Site selection
        ttk.Label(search_frame, text="Site:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.site_var = tk.StringVar(value="1337x")
        site_combo = ttk.Combobox(search_frame, textvariable=self.site_var, width=15)
        site_combo['values'] = ('1337x', 'piratebay', 'torrentgalaxy', 'rarbg', 'nyaa', 'yts', 'eztv')
        site_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        site_combo.state(['readonly'])

        # Recherche
        ttk.Label(search_frame, text="Recherche:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_torrents())

        # Bouton recherche
        search_btn = ttk.Button(search_frame, text="Rechercher", command=self.search_torrents)
        search_btn.grid(row=0, column=4, padx=(0, 10))

        # Barre de progression
        self.progress = ttk.Progressbar(search_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))

        # Frame des résultats
        results_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="5")
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Treeview pour les résultats
        columns = ('name', 'size', 'seeders', 'leechers', 'uploader', 'site')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)

        # Configuration des colonnes
        self.tree.heading('name', text='Nom du torrent')
        self.tree.heading('size', text='Taille')
        self.tree.heading('seeders', text='Seeders')
        self.tree.heading('leechers', text='Leechers')
        self.tree.heading('uploader', text='Uploader')
        self.tree.heading('site', text='Site')

        self.tree.column('name', width=400, anchor=tk.W)
        self.tree.column('size', width=100, anchor=tk.CENTER)
        self.tree.column('seeders', width=80, anchor=tk.CENTER)
        self.tree.column('leechers', width=80, anchor=tk.CENTER)
        self.tree.column('uploader', width=120, anchor=tk.CENTER)
        self.tree.column('site', width=80, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Placement
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Menu contextuel
        self.create_context_menu()

        # Bind double-click
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Prêt à rechercher...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)

    def create_context_menu(self):
        """Créer le menu contextuel"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copier le lien magnet", command=self.copy_magnet)
        self.context_menu.add_command(label="Ouvrir dans le navigateur", command=self.open_in_browser)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Télécharger avec le client par défaut", command=self.download_torrent)

    def show_context_menu(self, event):
        """Afficher le menu contextuel"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)

    def copy_magnet(self):
        """Copier le lien magnet dans le presse-papier"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.current_results):
                magnet = self.current_results[index]['magnet']
                self.root.clipboard_clear()
                self.root.clipboard_append(magnet)
                self.status_var.set("Lien magnet copié dans le presse-papier")

    def open_in_browser(self):
        """Ouvrir le lien dans le navigateur"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.current_results):
                url = self.current_results[index]['url']
                if url:
                    webbrowser.open(url)
                    self.status_var.set("Ouvert dans le navigateur")

    def download_torrent(self):
        """Télécharger avec le client torrent par défaut"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.current_results):
                magnet = self.current_results[index]['magnet']
                if magnet:
                    webbrowser.open(magnet)
                    self.status_var.set("Ouverture du client torrent...")

    def on_double_click(self, event):
        """Gérer le double-clic"""
        self.copy_magnet()

    def search_torrents(self):
        """Lancer une recherche de torrents"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer un terme de recherche")
            return

        site = self.site_var.get()

        # Démarrer la recherche dans un thread séparé
        thread = threading.Thread(target=self.run_search, args=(query, site))
        thread.daemon = True
        thread.start()

    def run_search(self, query: str, site: str):
        """Exécuter la recherche dans un thread séparé"""
        # Démarrer la barre de progression
        self.root.after(0, self.start_progress)
        self.root.after(0, lambda: self.status_var.set(f"Recherche de '{query}' sur {site}..."))

        # Créer une nouvelle boucle d'événements pour ce thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(self.api.search(query, site))
            self.root.after(0, lambda: self.display_results(results))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erreur lors de la recherche: {str(e)}"))
        finally:
            loop.close()
            self.root.after(0, self.stop_progress)

    def start_progress(self):
        """Démarrer la barre de progression"""
        self.progress.start()

    def stop_progress(self):
        """Arrêter la barre de progression"""
        self.progress.stop()

    def display_results(self, results: List[Dict]):
        """Afficher les résultats de recherche"""
        # Vider les résultats précédents
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.current_results = results

        # Ajouter les nouveaux résultats
        for result in results:
            self.tree.insert('', 'end', values=(
                result['name'][:80] + ('...' if len(result['name']) > 80 else ''),
                result['size'],
                result['seeders'],
                result['leechers'],
                result['uploader'],
                result['site']
            ))

        count = len(results)
        self.status_var.set(f"{count} torrent(s) trouvé(s)")

        if count == 0:
            messagebox.showinfo("Information", "Aucun résultat trouvé pour cette recherche")

    def show_error(self, message: str):
        """Afficher une erreur"""
        self.status_var.set("Erreur lors de la recherche")
        messagebox.showerror("Erreur", message)

    def on_closing(self):
        """Gérer la fermeture de l'application"""
        # Nettoyer les ressources
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.api.close_session())
        loop.close()

        self.root.destroy()

    def run(self):
        """Lancer l'application"""
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    try:
        app = TorrentSearchGUI()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")
        messagebox.showerror("Erreur", f"Impossible de lancer l'application: {e}")


if __name__ == "__main__":
    main()