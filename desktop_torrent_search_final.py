#!/usr/bin/env python3
"""
TorrentHunt Desktop - Version finale avec API réelle
Utilise l'API TorrentHunt officielle qui fonctionne !
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import aiohttp
import threading
import webbrowser
from urllib.parse import quote
import json
from typing import Dict, List, Optional
import time


class TorrentHuntAPI:
    """Client pour l'API TorrentHunt officielle"""

    def __init__(self):
        self.session = None
        self.base_url = "https://torrent-api-py-nx0x.onrender.com"
        self.sites = ["piratebay", "1337x", "torrentgalaxy", "rarbg", "nyaa", "yts", "eztv"]

    async def create_session(self):
        """Créer une session HTTP"""
        if not self.session:
            headers = {
                'User-Agent': 'TorrentHunt Desktop/1.0',
                'Accept': 'application/json',
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    async def close_session(self):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def search_site(self, query: str, site: str) -> List[Dict]:
        """Rechercher sur un site spécifique"""
        try:
            await self.create_session()

            url = f"{self.base_url}/api/v1/search"
            params = {
                "query": query,
                "site": site,
                "page": "1"
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    if "data" in data and data["data"]:
                        torrents = []
                        for item in data["data"][:15]:  # Limiter à 15 par site
                            torrents.append({
                                'name': item.get('name', 'Nom inconnu'),
                                'size': item.get('size', 'N/A'),
                                'seeders': int(item.get('seeders', 0)),
                                'leechers': int(item.get('leechers', 0)),
                                'uploader': item.get('uploader', 'Inconnu'),
                                'magnet': item.get('magnet', ''),
                                'url': item.get('url', ''),
                                'site': site,
                                'category': item.get('category', 'Autre'),
                                'date': item.get('date', '')
                            })
                        return torrents
                    else:
                        print(f"Aucun résultat pour {site}: {data}")
                        return []
                else:
                    print(f"Erreur HTTP {response.status} pour {site}")
                    return []

        except Exception as e:
            print(f"Erreur {site}: {e}")
            return []

    async def search_all_sites(self, query: str) -> List[Dict]:
        """Rechercher sur tous les sites en parallèle"""
        await self.create_session()

        # Lancer toutes les recherches en parallèle
        tasks = []
        for site in self.sites:
            task = self.search_site(query, site)
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_torrents = []
            for i, site_results in enumerate(results):
                if isinstance(site_results, list):
                    all_torrents.extend(site_results)
                    print(f"✓ {self.sites[i]}: {len(site_results)} résultats")
                elif isinstance(site_results, Exception):
                    print(f"✗ {self.sites[i]}: {site_results}")

            # Trier par nombre de seeders (décroissant)
            all_torrents.sort(key=lambda x: x.get('seeders', 0), reverse=True)

            print(f"Total: {len(all_torrents)} torrents trouvés")
            return all_torrents

        except Exception as e:
            print(f"Erreur recherche globale: {e}")
            return []


class TorrentHuntGUI:
    """Interface graphique TorrentHunt Desktop"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏴‍☠️ TorrentHunt Desktop - API Officielle")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)

        # Style
        self.setup_styles()

        # API client
        self.api = TorrentHuntAPI()
        self.current_results = []

        # Interface
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configuration des styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Couleurs personnalisées
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Stats.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='#27ae60')

        # Style Treeview
        style.configure('Treeview', rowheight=28, font=('Arial', 9))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def create_widgets(self):
        """Créer l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuration grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # En-tête
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(header_frame, text="🏴‍☠️ TorrentHunt Desktop", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(header_frame, text="API Officielle • Recherche Multi-Sites",
                                 font=('Arial', 10, 'italic'), foreground='#95a5a6')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

        # Frame de recherche
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Recherche Torrent", padding="15")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        search_frame.columnconfigure(1, weight=1)

        # Champ de recherche
        ttk.Label(search_frame, text="Terme de recherche:", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 15)
        )

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=60, font=('Arial', 11))
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 15))
        search_entry.bind('<Return>', lambda e: self.search_torrents())

        # Bouton de recherche
        search_btn = ttk.Button(search_frame, text="🚀 Rechercher sur tous les sites",
                               command=self.search_torrents)
        search_btn.grid(row=0, column=2)

        # Sites disponibles
        sites_label = ttk.Label(search_frame, text="Sites: PirateBay • 1337x • TorrentGalaxy • RARBG • Nyaa • YTS • EZTV",
                               style='Stats.TLabel')
        sites_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

        # Barre de progression
        progress_frame = ttk.Frame(search_frame)
        progress_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Frame des résultats
        results_frame = ttk.LabelFrame(main_frame, text="📊 Résultats (triés par popularité)", padding="5")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Treeview avec colonnes optimisées
        columns = ('name', 'site', 'size', 'seeders', 'leechers', 'date')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=20)

        # Configuration des colonnes
        self.tree.heading('name', text='📁 Nom du torrent')
        self.tree.heading('site', text='🌐 Site')
        self.tree.heading('size', text='💾 Taille')
        self.tree.heading('seeders', text='🔼 Seeders')
        self.tree.heading('leechers', text='🔽 Leechers')
        self.tree.heading('date', text='📅 Date')

        # Largeurs des colonnes
        self.tree.column('name', width=500, anchor=tk.W)
        self.tree.column('site', width=120, anchor=tk.CENTER)
        self.tree.column('size', width=100, anchor=tk.CENTER)
        self.tree.column('seeders', width=80, anchor=tk.CENTER)
        self.tree.column('leechers', width=80, anchor=tk.CENTER)
        self.tree.column('date', width=100, anchor=tk.CENTER)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Placement
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Menu contextuel
        self.create_context_menu()

        # Events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        status_frame.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="🟢 Prêt à rechercher des torrents...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10))
        status_label.grid(row=0, column=0, sticky=tk.W)

    def create_context_menu(self):
        """Créer le menu contextuel"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📋 Copier le lien magnet", command=self.copy_magnet)
        self.context_menu.add_command(label="🌐 Ouvrir dans le navigateur", command=self.open_in_browser)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⬇️ Télécharger avec client torrent", command=self.download_torrent)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="ℹ️ Afficher les détails", command=self.show_details)

    def show_context_menu(self, event):
        """Afficher le menu contextuel"""
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def copy_magnet(self):
        """Copier le lien magnet"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            if index < len(self.current_results):
                magnet = self.current_results[index]['magnet']
                if magnet:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(magnet)
                    self.status_var.set("✅ Lien magnet copié dans le presse-papier")
                else:
                    messagebox.showwarning("Attention", "Aucun lien magnet disponible")

    def open_in_browser(self):
        """Ouvrir dans le navigateur"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            if index < len(self.current_results):
                url = self.current_results[index]['url']
                if url:
                    webbrowser.open(url)
                    self.status_var.set("🌐 Ouvert dans le navigateur")
                else:
                    messagebox.showwarning("Attention", "Aucune URL disponible")

    def download_torrent(self):
        """Télécharger avec le client torrent"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            if index < len(self.current_results):
                magnet = self.current_results[index]['magnet']
                if magnet:
                    webbrowser.open(magnet)
                    self.status_var.set("⬇️ Ouverture du client torrent...")
                else:
                    messagebox.showwarning("Attention", "Aucun lien magnet disponible")

    def show_details(self):
        """Afficher les détails du torrent"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            if index < len(self.current_results):
                torrent = self.current_results[index]

                details = f"""
🏴‍☠️ DÉTAILS DU TORRENT

📁 Nom: {torrent['name']}
🌐 Site: {torrent['site'].upper()}
💾 Taille: {torrent['size']}
🔼 Seeders: {torrent['seeders']}
🔽 Leechers: {torrent['leechers']}
👤 Uploader: {torrent['uploader']}
📂 Catégorie: {torrent['category']}
📅 Date: {torrent['date']}

🔗 URL: {torrent['url']}

🧲 Magnet Link:
{torrent['magnet'][:100]}...
                """

                messagebox.showinfo("Détails du torrent", details)

    def on_double_click(self, event):
        """Gérer le double-clic"""
        self.copy_magnet()

    def search_torrents(self):
        """Lancer la recherche"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer un terme de recherche")
            return

        if len(query) < 2:
            messagebox.showwarning("Attention", "Le terme de recherche doit contenir au moins 2 caractères")
            return

        # Nettoyer les résultats précédents
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Démarrer la recherche dans un thread
        thread = threading.Thread(target=self.run_search, args=(query,))
        thread.daemon = True
        thread.start()

    def run_search(self, query: str):
        """Exécuter la recherche dans un thread séparé"""
        self.root.after(0, self.start_progress)
        self.root.after(0, lambda: self.status_var.set(f"🔍 Recherche de '{query}' sur 7 sites..."))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            start_time = time.time()
            results = loop.run_until_complete(self.api.search_all_sites(query))
            end_time = time.time()

            search_time = end_time - start_time
            self.root.after(0, lambda: self.display_results(results, query, search_time))

        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erreur lors de la recherche: {str(e)}"))
        finally:
            loop.close()
            self.root.after(0, self.stop_progress)

    def start_progress(self):
        """Démarrer la barre de progression"""
        self.progress.start(10)

    def stop_progress(self):
        """Arrêter la barre de progression"""
        self.progress.stop()

    def display_results(self, results: List[Dict], query: str, search_time: float):
        """Afficher les résultats"""
        self.current_results = results

        if not results:
            self.status_var.set("❌ Aucun résultat trouvé")
            messagebox.showinfo("Aucun résultat",
                              f"Aucun torrent trouvé pour '{query}'.\n\n" +
                              "Suggestions:\n" +
                              "• Vérifiez l'orthographe\n" +
                              "• Essayez des termes plus génériques\n" +
                              "• Utilisez des mots-clés en anglais")
            return

        # Compter par site
        sites_count = {}
        for result in results:
            site = result['site']
            sites_count[site] = sites_count.get(site, 0) + 1

        # Ajouter les résultats au treeview
        for i, result in enumerate(results):
            # Icônes par site
            site_icons = {
                "piratebay": "🏴‍☠️", "1337x": "🔥", "torrentgalaxy": "🌌",
                "rarbg": "💎", "nyaa": "🎌", "yts": "🎬", "eztv": "📺"
            }

            site_icon = site_icons.get(result['site'], "🌐")

            # Couleurs alternées
            tags = ('oddrow',) if i % 2 == 0 else ('evenrow',)

            values = (
                result['name'][:85] + ('...' if len(result['name']) > 85 else ''),
                f"{site_icon} {result['site']}",
                result['size'],
                f"{result['seeders']}",
                f"{result['leechers']}",
                result['date']
            )

            self.tree.insert('', 'end', values=values, tags=tags)

        # Style des lignes
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='#ffffff')

        # Statistiques
        total = len(results)
        sites_info = " • ".join([f"{site}: {count}" for site, count in sites_count.items()])

        self.status_var.set(f"✅ {total} torrents trouvés en {search_time:.1f}s - {sites_info}")

    def show_error(self, message: str):
        """Afficher une erreur"""
        self.status_var.set("❌ Erreur lors de la recherche")
        messagebox.showerror("Erreur", message)

    def on_closing(self):
        """Fermer l'application proprement"""
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
        print("🏴‍☠️ Lancement de TorrentHunt Desktop...")
        print("API: https://torrent-api-py-nx0x.onrender.com")

        app = TorrentHuntGUI()
        app.run()

    except Exception as e:
        print(f"Erreur fatale: {e}")
        messagebox.showerror("Erreur", f"Impossible de lancer l'application:\n{e}")


if __name__ == "__main__":
    main()