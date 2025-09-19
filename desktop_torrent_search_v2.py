#!/usr/bin/env python3
"""
Application desktop pour rechercher des torrents - Version améliorée
Recherche réelle sur tous les sites simultanément
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import asyncio
import aiohttp
import threading
import webbrowser
from urllib.parse import quote, urljoin
import json
from typing import Dict, List, Optional
import re
from bs4 import BeautifulSoup
import time


class TorrentSearchAPI:
    """API client pour rechercher des torrents sur tous les sites"""

    def __init__(self):
        self.session = None
        self.sites_config = {
            "1337x": {
                "name": "1337x",
                "search_url": "https://1337x.to/search/{query}/1/",
                "color": "#ff6b6b"
            },
            "piratebay": {
                "name": "ThePirateBay",
                "search_url": "https://thepiratebay.org/search.php?q={query}",
                "color": "#4ecdc4"
            },
            "nyaa": {
                "name": "Nyaa",
                "search_url": "https://nyaa.si/?q={query}",
                "color": "#45b7d1"
            },
            "rarbg": {
                "name": "RARBG",
                "search_url": "https://rargb.to/search/?search={query}",
                "color": "#f9ca24"
            },
            "torrentgalaxy": {
                "name": "TorrentGalaxy",
                "search_url": "https://torrentgalaxy.to/torrents.php?search={query}",
                "color": "#6c5ce7"
            },
            "yts": {
                "name": "YTS",
                "search_url": "https://yts.mx/browse-movies/{query}",
                "color": "#a29bfe"
            }
        }

    async def create_session(self):
        """Créer une session HTTP avec headers réalistes"""
        if not self.session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300, use_dns_cache=True)
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=timeout
            )

    async def close_session(self):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def search_1337x(self, query: str) -> List[Dict]:
        """Recherche réelle sur 1337x"""
        try:
            # Utiliser py1337x pour une recherche fiable
            from py1337x import AsyncPy1337x
            py1337x = AsyncPy1337x()
            results = await py1337x.search(query, page=1)

            torrents = []
            if results and 'items' in results:
                for item in results['items'][:15]:
                    name = item.get('name', 'Nom non disponible')
                    # Nettoyer le nom
                    name = re.sub(r'\[.*?\]', '', name).strip()

                    torrents.append({
                        'name': name,
                        'size': item.get('size', 'N/A'),
                        'seeders': int(item.get('seeders', 0)),
                        'leechers': int(item.get('leechers', 0)),
                        'uploader': item.get('uploader', 'Inconnu'),
                        'magnet': item.get('magnetLink', ''),
                        'url': item.get('link', ''),
                        'site': '1337x',
                        'category': item.get('category', 'Autre')
                    })
            return torrents
        except Exception as e:
            print(f"Erreur 1337x: {e}")
            return []

    async def search_nyaa(self, query: str) -> List[Dict]:
        """Recherche réelle sur Nyaa"""
        try:
            if not self.session:
                await self.create_session()

            url = f"https://nyaa.si/?q={quote(query)}&f=0&c=0_0"

            async with self.session.get(url) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                torrents = []
                rows = soup.select('tbody tr')

                for row in rows[:10]:
                    try:
                        cols = row.find_all('td')
                        if len(cols) < 6:
                            continue

                        # Nom du torrent
                        name_link = cols[1].find('a', attrs={'href': lambda x: x and '/view/' in x})
                        name = name_link.get_text().strip() if name_link else "Nom inconnu"

                        # Lien
                        torrent_url = urljoin("https://nyaa.si", name_link.get('href')) if name_link else ""

                        # Magnet link
                        magnet_link = cols[2].find('a', attrs={'href': lambda x: x and x.startswith('magnet:')})
                        magnet = magnet_link.get('href') if magnet_link else ""

                        # Taille
                        size = cols[3].get_text().strip()

                        # Seeders/Leechers
                        seeders = int(cols[5].get_text().strip() or 0)
                        leechers = int(cols[6].get_text().strip() or 0)

                        torrents.append({
                            'name': name,
                            'size': size,
                            'seeders': seeders,
                            'leechers': leechers,
                            'uploader': 'Nyaa User',
                            'magnet': magnet,
                            'url': torrent_url,
                            'site': 'nyaa',
                            'category': 'Anime'
                        })
                    except Exception as e:
                        continue

                return torrents
        except Exception as e:
            print(f"Erreur Nyaa: {e}")
            return []

    async def search_torrentgalaxy(self, query: str) -> List[Dict]:
        """Recherche réelle sur TorrentGalaxy"""
        try:
            if not self.session:
                await self.create_session()

            url = f"https://torrentgalaxy.to/torrents.php?search={quote(query)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                torrents = []
                rows = soup.select('div.tgxtablerow')

                for row in rows[:10]:
                    try:
                        # Nom
                        name_elem = row.select_one('div.tgxtablecell:nth-child(4) a')
                        name = name_elem.get_text().strip() if name_elem else "Nom inconnu"

                        # URL
                        url_link = urljoin("https://torrentgalaxy.to", name_elem.get('href')) if name_elem else ""

                        # Magnet
                        magnet_elem = row.select_one('a[href^="magnet:"]')
                        magnet = magnet_elem.get('href') if magnet_elem else ""

                        # Taille
                        size_elem = row.select_one('div.tgxtablecell:nth-child(8)')
                        size = size_elem.get_text().strip() if size_elem else "N/A"

                        # Seeders
                        seeders_elem = row.select_one('font[color="green"]')
                        seeders = int(seeders_elem.get_text().strip() or 0) if seeders_elem else 0

                        # Leechers
                        leechers_elem = row.select_one('font[color="#ff0000"]')
                        leechers = int(leechers_elem.get_text().strip() or 0) if leechers_elem else 0

                        torrents.append({
                            'name': name,
                            'size': size,
                            'seeders': seeders,
                            'leechers': leechers,
                            'uploader': 'TG User',
                            'magnet': magnet,
                            'url': url_link,
                            'site': 'torrentgalaxy',
                            'category': 'Divers'
                        })
                    except Exception as e:
                        continue

                return torrents
        except Exception as e:
            print(f"Erreur TorrentGalaxy: {e}")
            return []

    async def search_all_sites(self, query: str) -> List[Dict]:
        """Rechercher sur tous les sites simultanément"""
        await self.create_session()

        # Lancer toutes les recherches en parallèle
        tasks = [
            self.search_1337x(query),
            self.search_nyaa(query),
            self.search_torrentgalaxy(query),
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combiner tous les résultats
            all_torrents = []
            for site_results in results:
                if isinstance(site_results, list):
                    all_torrents.extend(site_results)
                elif isinstance(site_results, Exception):
                    print(f"Erreur sur un site: {site_results}")

            # Trier par nombre de seeders (décroissant)
            all_torrents.sort(key=lambda x: x.get('seeders', 0), reverse=True)

            return all_torrents[:50]  # Limiter à 50 résultats

        except Exception as e:
            print(f"Erreur recherche globale: {e}")
            return []


class TorrentSearchGUI:
    """Interface graphique améliorée pour rechercher des torrents"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TorrentHunt Desktop v2 - Recherche Multi-Sites")
        self.root.geometry("1400x800")
        self.root.minsize(900, 600)

        # Style
        self.setup_styles()

        # API client
        self.api = TorrentSearchAPI()

        # Variables
        self.current_results = []
        self.search_stats = {"total": 0, "sites": {}}

        # Interface
        self.create_widgets()

        # Configuration de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configuration des styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Couleurs et polices
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Stats.TLabel', font=('Arial', 10), foreground='#7f8c8d')

        # Style pour le Treeview
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def create_widgets(self):
        """Créer les widgets de l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Titre avec icône
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(title_frame, text="🔍 TorrentHunt Desktop v2", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(title_frame, text="Recherche simultanée sur tous les sites",
                                 font=('Arial', 10, 'italic'), foreground='#95a5a6')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

        # Frame de recherche
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Recherche Multi-Sites", padding="15")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        search_frame.columnconfigure(1, weight=1)

        # Champ de recherche
        ttk.Label(search_frame, text="Recherche:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50, font=('Arial', 11))
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 15))
        search_entry.bind('<Return>', lambda e: self.search_torrents())

        # Bouton recherche stylé
        search_btn = ttk.Button(search_frame, text="🚀 Rechercher sur tous les sites",
                               command=self.search_torrents)
        search_btn.grid(row=0, column=2, padx=(0, 10))

        # Barre de progression avec texte
        progress_frame = ttk.Frame(search_frame)
        progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.progress_label = ttk.Label(progress_frame, text="", font=('Arial', 9, 'italic'))
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Statistiques
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.stats_label = ttk.Label(stats_frame, text="Prêt à rechercher...", style='Stats.TLabel')
        self.stats_label.pack(side=tk.LEFT)

        # Frame des résultats
        results_frame = ttk.LabelFrame(main_frame, text="📊 Résultats (triés par popularité)", padding="5")
        results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Treeview amélioré
        columns = ('name', 'site', 'size', 'seeders', 'leechers', 'uploader')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=18)

        # Configuration des colonnes avec icônes
        self.tree.heading('name', text='📁 Nom du torrent')
        self.tree.heading('site', text='🌐 Site')
        self.tree.heading('size', text='💾 Taille')
        self.tree.heading('seeders', text='🔼 Seeders')
        self.tree.heading('leechers', text='🔽 Leechers')
        self.tree.heading('uploader', text='👤 Uploader')

        # Largeurs optimisées
        self.tree.column('name', width=500, anchor=tk.W)
        self.tree.column('site', width=120, anchor=tk.CENTER)
        self.tree.column('size', width=100, anchor=tk.CENTER)
        self.tree.column('seeders', width=80, anchor=tk.CENTER)
        self.tree.column('leechers', width=80, anchor=tk.CENTER)
        self.tree.column('uploader', width=150, anchor=tk.CENTER)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Placement avec scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Menu contextuel
        self.create_context_menu()

        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Status bar améliorée
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="🟢 Prêt à rechercher sur tous les sites...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 9))
        status_label.grid(row=0, column=0, sticky=tk.W)

    def create_context_menu(self):
        """Créer le menu contextuel amélioré"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📋 Copier le lien magnet", command=self.copy_magnet)
        self.context_menu.add_command(label="🌐 Ouvrir dans le navigateur", command=self.open_in_browser)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⬇️ Télécharger avec le client torrent", command=self.download_torrent)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="ℹ️ Informations détaillées", command=self.show_torrent_info)

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
                if magnet:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(magnet)
                    self.status_var.set("✅ Lien magnet copié dans le presse-papier")
                else:
                    messagebox.showwarning("Attention", "Aucun lien magnet disponible pour ce torrent")

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
                    self.status_var.set("🌐 Ouvert dans le navigateur")
                else:
                    messagebox.showwarning("Attention", "Aucune URL disponible")

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
                    self.status_var.set("⬇️ Ouverture du client torrent...")
                else:
                    messagebox.showwarning("Attention", "Aucun lien magnet disponible")

    def show_torrent_info(self):
        """Afficher les informations détaillées du torrent"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if index < len(self.current_results):
                torrent = self.current_results[index]

                info_text = f"""
📁 Nom: {torrent['name']}
🌐 Site: {torrent['site']}
💾 Taille: {torrent['size']}
🔼 Seeders: {torrent['seeders']}
🔽 Leechers: {torrent['leechers']}
👤 Uploader: {torrent['uploader']}
📂 Catégorie: {torrent.get('category', 'N/A')}
🔗 URL: {torrent['url']}
🧲 Magnet: {torrent['magnet'][:100]}...
                """

                messagebox.showinfo("Informations du torrent", info_text)

    def on_double_click(self, event):
        """Gérer le double-clic - copier le magnet"""
        self.copy_magnet()

    def search_torrents(self):
        """Lancer une recherche de torrents sur tous les sites"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer un terme de recherche")
            return

        # Démarrer la recherche dans un thread séparé
        thread = threading.Thread(target=self.run_search, args=(query,))
        thread.daemon = True
        thread.start()

    def run_search(self, query: str):
        """Exécuter la recherche dans un thread séparé"""
        # Démarrer la progression
        self.root.after(0, self.start_progress)
        self.root.after(0, lambda: self.status_var.set(f"🔍 Recherche de '{query}' sur tous les sites..."))
        self.root.after(0, lambda: self.progress_label.config(text="Connexion aux sites de torrents..."))

        # Créer une nouvelle boucle d'événements
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Mise à jour du statut
            self.root.after(0, lambda: self.progress_label.config(text="Recherche en cours sur 1337x, Nyaa, TorrentGalaxy..."))

            results = loop.run_until_complete(self.api.search_all_sites(query))
            self.root.after(0, lambda: self.display_results(results, query))
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
        self.progress_label.config(text="")

    def display_results(self, results: List[Dict], query: str):
        """Afficher les résultats de recherche"""
        # Vider les résultats précédents
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.current_results = results

        # Compter par site
        site_counts = {}
        for result in results:
            site = result['site']
            site_counts[site] = site_counts.get(site, 0) + 1

        # Ajouter les nouveaux résultats avec couleurs alternées
        for i, result in enumerate(results):
            # Couleur de ligne alternée
            tags = ('oddrow',) if i % 2 == 0 else ('evenrow',)

            # Icône selon le site
            site_icon = {"1337x": "🔥", "nyaa": "🎌", "torrentgalaxy": "🌌"}.get(result['site'], "🌐")

            values = (
                result['name'][:100] + ('...' if len(result['name']) > 100 else ''),
                f"{site_icon} {result['site']}",
                result['size'],
                f"{result['seeders']} 🔼",
                f"{result['leechers']} 🔽",
                result['uploader'][:20]
            )

            self.tree.insert('', 'end', values=values, tags=tags)

        # Configuration des couleurs
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='#ffffff')

        # Mise à jour des statistiques
        count = len(results)
        sites_info = ", ".join([f"{site}: {count}" for site, count in site_counts.items()])

        self.stats_label.config(text=f"📊 {count} torrents trouvés - {sites_info}")
        self.status_var.set(f"✅ Recherche terminée - {count} résultats pour '{query}'")

        if count == 0:
            messagebox.showinfo("Information",
                              "Aucun résultat trouvé.\n\nVérifiez:\n" +
                              "• L'orthographe du terme de recherche\n" +
                              "• Votre connexion internet\n" +
                              "• Les sites peuvent être temporairement indisponibles")

    def show_error(self, message: str):
        """Afficher une erreur"""
        self.status_var.set("❌ Erreur lors de la recherche")
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