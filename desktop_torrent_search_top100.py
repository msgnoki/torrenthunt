#!/usr/bin/env python3
"""
TorrentHunt Desktop - Version avec Top 100 par catégories
Recherche + Top 100 (Audio, Video, Books, etc.)
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
    """Client pour l'API TorrentHunt avec Top 100"""

    def __init__(self):
        self.base_url = "https://torrent-api-py-nx0x.onrender.com"
        self.sites_info = {
            "piratebay": {"name": "ThePirateBay", "icon": "🏴‍☠️", "color": "#e74c3c"},
            "1337x": {"name": "1337x", "icon": "🔥", "color": "#f39c12"},
            "torrentgalaxy": {"name": "TorrentGalaxy", "icon": "🌌", "color": "#9b59b6"},
            "rarbg": {"name": "RARBG", "icon": "💎", "color": "#3498db"},
            "nyaa": {"name": "Nyaa", "icon": "🎌", "color": "#e91e63"},
            "yts": {"name": "YTS", "icon": "🎬", "color": "#2ecc71"},
            "eztv": {"name": "EZTV", "icon": "📺", "color": "#34495e"}
        }

        self.categories = {
            "all": {"name": "Tous", "icon": "🌟"},
            "audio": {"name": "Audio/Musique", "icon": "🎵"},
            "video": {"name": "Vidéo/Films", "icon": "🎬"},
            "tv": {"name": "Séries TV", "icon": "📺"},
            "books": {"name": "Livres/eBooks", "icon": "📚"},
            "games": {"name": "Jeux", "icon": "🎮"},
            "software": {"name": "Logiciels", "icon": "💻"},
            "anime": {"name": "Anime", "icon": "🎌"}
        }

    async def create_fresh_session(self):
        """Créer une nouvelle session HTTP fraîche"""
        headers = {
            'User-Agent': 'TorrentHunt Desktop Top100/1.0',
            'Accept': 'application/json',
            'Connection': 'close'
        }

        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=60,
            use_dns_cache=True,
            keepalive_timeout=10,
            enable_cleanup_closed=True
        )

        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        session = aiohttp.ClientSession(
            connector=connector,
            headers=headers,
            timeout=timeout
        )
        return session

    async def search_torrents(self, query: str, sites: List[str], category: str = "all") -> List[Dict]:
        """Rechercher des torrents"""
        all_results = []

        # Créer une nouvelle session pour cette recherche
        session = await self.create_fresh_session()

        try:
            for site in sites:
                try:
                    params = {
                        "query": query,
                        "site": site,
                        "limit": 20
                    }
                    if category != "all":
                        params["category"] = category

                    url = f"{self.base_url}/api/v1/search"
                    print(f"🔍 Recherche sur {site}: {url}")

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = data.get("data", [])

                            for result in results:
                                result["source_site"] = site
                                result["source_icon"] = self.sites_info.get(site, {}).get("icon", "🔗")
                                result["source_name"] = self.sites_info.get(site, {}).get("name", site)
                                all_results.append(result)

                            print(f"✅ {site}: {len(results)} résultats")
                        else:
                            print(f"❌ {site}: HTTP {response.status}")

                except Exception as e:
                    print(f"❌ Erreur {site}: {e}")
                    continue

        finally:
            # Fermer la session proprement
            await session.close()
            print("🔒 Session fermée")

        return all_results

    async def get_top_torrents(self, sites: List[str], category: str = "all", limit: int = 50) -> List[Dict]:
        """Récupérer le top des torrents par catégorie"""
        all_results = []

        # Créer une nouvelle session pour cette requête
        session = await self.create_fresh_session()

        try:
            for site in sites:
                try:
                    params = {
                        "site": site,
                        "limit": limit
                    }

                    # Utiliser l'endpoint trending
                    url = f"{self.base_url}/api/v1/trending"
                    print(f"📈 Top {site}: {url}")

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = data.get("data", [])

                            # Filtrer par catégorie si nécessaire
                            if category != "all":
                                filtered_results = []
                                for result in results:
                                    torrent_category = result.get("category", "").lower()
                                    torrent_name = result.get("name", "").lower()

                                    # Logique de filtrage par catégorie
                                    if self._matches_category(torrent_name, torrent_category, category):
                                        filtered_results.append(result)

                                results = filtered_results[:limit//len(sites)]  # Limiter par site

                            for result in results:
                                result["source_site"] = site
                                result["source_icon"] = self.sites_info.get(site, {}).get("icon", "🔗")
                                result["source_name"] = self.sites_info.get(site, {}).get("name", site)
                                all_results.append(result)

                            print(f"✅ {site}: {len(results)} résultats top")
                        else:
                            print(f"❌ {site}: HTTP {response.status}")

                except Exception as e:
                    print(f"❌ Erreur top {site}: {e}")
                    continue

        finally:
            # Fermer la session proprement
            await session.close()
            print("🔒 Session top fermée")

        return all_results

    def _matches_category(self, name: str, torrent_category: str, target_category: str) -> bool:
        """Vérifier si un torrent correspond à la catégorie"""
        name = name.lower()
        torrent_category = torrent_category.lower()

        if target_category == "audio":
            return any(word in name or word in torrent_category for word in
                      ["music", "audio", "mp3", "flac", "album", "song", "musique"])
        elif target_category == "video":
            return any(word in name or word in torrent_category for word in
                      ["movie", "film", "video", "mp4", "mkv", "avi", "cinema"])
        elif target_category == "tv":
            return any(word in name or word in torrent_category for word in
                      ["tv", "series", "episode", "season", "s01", "s02", "série"])
        elif target_category == "books":
            return any(word in name or word in torrent_category for word in
                      ["book", "ebook", "pdf", "epub", "livre", "magazine"])
        elif target_category == "games":
            return any(word in name or word in torrent_category for word in
                      ["game", "pc", "xbox", "playstation", "nintendo", "jeu"])
        elif target_category == "software":
            return any(word in name or word in torrent_category for word in
                      ["software", "app", "program", "windows", "mac", "linux"])
        elif target_category == "anime":
            return any(word in name or word in torrent_category for word in
                      ["anime", "manga", "japanese", "subbed", "dubbed"])

        return True  # Si pas de filtre spécifique


class TorrentHuntGUI:
    """Interface graphique avec onglets Recherche et Top 100"""

    def __init__(self):
        self.api = TorrentHuntAPI()
        self.setup_gui()
        self.results = []
        self.sort_column = None
        self.sort_reverse = False

    def setup_gui(self):
        """Créer l'interface principale avec onglets"""
        self.root = tk.Tk()
        self.root.title("🏴‍☠️ TorrentHunt Desktop - Top 100")
        self.root.geometry("1200x700")

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Onglet Recherche
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="🔍 Recherche")
        self.setup_search_tab()

        # Onglet Top 100
        self.top_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.top_frame, text="📈 Top 100")
        self.setup_top_tab()

        # Créer l'arbre des résultats (partagé)
        self.setup_results_tree()

    def setup_search_tab(self):
        """Configurer l'onglet de recherche"""
        # Frame de recherche
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="🔍 Recherche:", font=("Arial", 12, "bold")).pack(anchor="w")

        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill="x", pady=5)

        self.search_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.start_search())

        self.search_button = ttk.Button(input_frame, text="Rechercher", command=self.start_search)
        self.search_button.pack(side="right")

        # Sites selection pour recherche
        sites_frame = ttk.LabelFrame(search_frame, text="🌐 Sites à inclure", padding=10)
        sites_frame.pack(fill="x", pady=5)

        self.search_site_vars = {}
        sites_grid = ttk.Frame(sites_frame)
        sites_grid.pack(fill="x")

        for i, (site_key, site_info) in enumerate(self.api.sites_info.items()):
            var = tk.BooleanVar(value=True)
            self.search_site_vars[site_key] = var

            cb = ttk.Checkbutton(sites_grid,
                               text=f"{site_info['icon']} {site_info['name']}",
                               variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=2)

        # Boutons sélection pour recherche
        btn_frame = ttk.Frame(sites_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Tout sélectionner",
                  command=lambda: self.toggle_all_sites(True, 'search')).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Tout déselectionner",
                  command=lambda: self.toggle_all_sites(False, 'search')).pack(side="left", padx=5)

        # Status pour recherche
        self.search_status = ttk.Label(search_frame, text="Prêt pour la recherche",
                                      foreground="green", font=("Arial", 10))
        self.search_status.pack(anchor="w", pady=5)

    def setup_top_tab(self):
        """Configurer l'onglet Top 100"""
        # Frame de contrôles Top 100
        top_controls = ttk.Frame(self.top_frame)
        top_controls.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_controls, text="📈 Top 100:", font=("Arial", 12, "bold")).pack(anchor="w")

        # Sélection de catégorie
        cat_frame = ttk.Frame(top_controls)
        cat_frame.pack(fill="x", pady=5)

        ttk.Label(cat_frame, text="Catégorie:").pack(side="left", padx=(0, 10))
        self.category_combo = ttk.Combobox(cat_frame, width=20, state="readonly")
        self.category_combo.pack(side="left", padx=(0, 10))

        # Remplir les catégories
        categories = [f"{info['icon']} {info['name']}" for info in self.api.categories.values()]
        self.category_combo['values'] = categories
        self.category_combo.set(categories[0])  # "Tous" par défaut

        self.top_button = ttk.Button(cat_frame, text="Charger Top 100", command=self.start_top_load)
        self.top_button.pack(side="left", padx=10)

        # Sites selection pour top
        top_sites_frame = ttk.LabelFrame(top_controls, text="🌐 Sites pour Top 100", padding=10)
        top_sites_frame.pack(fill="x", pady=5)

        self.top_site_vars = {}
        top_sites_grid = ttk.Frame(top_sites_frame)
        top_sites_grid.pack(fill="x")

        for i, (site_key, site_info) in enumerate(self.api.sites_info.items()):
            var = tk.BooleanVar(value=True)
            self.top_site_vars[site_key] = var

            cb = ttk.Checkbutton(top_sites_grid,
                               text=f"{site_info['icon']} {site_info['name']}",
                               variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=2)

        # Boutons sélection pour top
        top_btn_frame = ttk.Frame(top_sites_frame)
        top_btn_frame.pack(fill="x", pady=5)

        ttk.Button(top_btn_frame, text="Tout sélectionner",
                  command=lambda: self.toggle_all_sites(True, 'top')).pack(side="left", padx=5)
        ttk.Button(top_btn_frame, text="Tout déselectionner",
                  command=lambda: self.toggle_all_sites(False, 'top')).pack(side="left", padx=5)

        # Status pour top
        self.top_status = ttk.Label(top_controls, text="Prêt pour charger le Top 100",
                                   foreground="green", font=("Arial", 10))
        self.top_status.pack(anchor="w", pady=5)

    def setup_results_tree(self):
        """Configurer l'arbre des résultats (en bas de la fenêtre)"""
        # Frame principal pour l'arbre (en bas de la fenêtre, sous les onglets)
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Treeview avec scrollbars
        columns = ("name", "size", "seeders", "leechers", "source")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # En-têtes cliquables pour tri
        self.tree.heading("name", text="📄 Nom", command=lambda: self.sort_by_column("name"))
        self.tree.heading("size", text="💾 Taille", command=lambda: self.sort_by_column("size"))
        self.tree.heading("seeders", text="🌱 Seeders", command=lambda: self.sort_by_column("seeders"))
        self.tree.heading("leechers", text="📥 Leechers", command=lambda: self.sort_by_column("leechers"))
        self.tree.heading("source", text="🌐 Source", command=lambda: self.sort_by_column("source"))

        # Largeurs des colonnes
        self.tree.column("name", width=400, minwidth=200)
        self.tree.column("size", width=100, minwidth=80)
        self.tree.column("seeders", width=80, minwidth=60)
        self.tree.column("leechers", width=80, minwidth=60)
        self.tree.column("source", width=120, minwidth=100)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Double-clic pour ouvrir magnet
        self.tree.bind("<Double-1>", self.open_magnet)

    def toggle_all_sites(self, select_all: bool, tab_type: str):
        """Sélectionner/désélectionner tous les sites"""
        site_vars = self.search_site_vars if tab_type == 'search' else self.top_site_vars
        for var in site_vars.values():
            var.set(select_all)

    def get_selected_sites(self, tab_type: str) -> List[str]:
        """Obtenir la liste des sites sélectionnés"""
        site_vars = self.search_site_vars if tab_type == 'search' else self.top_site_vars
        return [site for site, var in site_vars.items() if var.get()]

    def start_search(self):
        """Démarrer une recherche en arrière-plan"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez saisir un terme de recherche")
            return

        selected_sites = self.get_selected_sites('search')
        if not selected_sites:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un site")
            return

        self.search_button.config(state="disabled")
        self.search_status.config(text="🔍 Recherche en cours...", foreground="orange")

        # Nettoyer les résultats précédents
        self.clear_results()

        # Lancer la recherche en arrière-plan
        thread = threading.Thread(target=self.search_thread, args=(query, selected_sites))
        thread.daemon = True
        thread.start()

    def start_top_load(self):
        """Démarrer le chargement du Top 100"""
        selected_sites = self.get_selected_sites('top')
        if not selected_sites:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un site")
            return

        # Obtenir la catégorie sélectionnée
        category_text = self.category_combo.get()
        category_key = "all"
        for key, info in self.api.categories.items():
            if f"{info['icon']} {info['name']}" == category_text:
                category_key = key
                break

        self.top_button.config(state="disabled")
        self.top_status.config(text="📈 Chargement du Top 100...", foreground="orange")

        # Nettoyer les résultats précédents
        self.clear_results()

        # Lancer le chargement en arrière-plan
        thread = threading.Thread(target=self.top_thread, args=(selected_sites, category_key))
        thread.daemon = True
        thread.start()

    def search_thread(self, query: str, sites: List[str]):
        """Thread de recherche"""
        try:
            # Créer une nouvelle boucle asyncio pour ce thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(self.api.search_torrents(query, sites))

            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, self.update_search_results, results)

        except Exception as e:
            error_msg = f"Erreur de recherche: {e}"
            print(error_msg)
            self.root.after(0, self.update_search_error, error_msg)
        finally:
            loop.close()

    def top_thread(self, sites: List[str], category: str):
        """Thread de chargement Top 100"""
        try:
            # Créer une nouvelle boucle asyncio pour ce thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(self.api.get_top_torrents(sites, category))

            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, self.update_top_results, results)

        except Exception as e:
            error_msg = f"Erreur Top 100: {e}"
            print(error_msg)
            self.root.after(0, self.update_top_error, error_msg)
        finally:
            loop.close()

    def update_search_results(self, results: List[Dict]):
        """Mettre à jour les résultats de recherche"""
        self.results = results
        self.populate_tree()

        count = len(results)
        self.search_status.config(text=f"✅ {count} torrents trouvés", foreground="green")
        self.search_button.config(state="normal")

    def update_top_results(self, results: List[Dict]):
        """Mettre à jour les résultats Top 100"""
        self.results = results
        self.populate_tree()

        count = len(results)
        category_name = self.category_combo.get()
        self.top_status.config(text=f"✅ Top {count} - {category_name}", foreground="green")
        self.top_button.config(state="normal")

    def update_search_error(self, error_msg: str):
        """Mettre à jour en cas d'erreur de recherche"""
        self.search_status.config(text=f"❌ {error_msg}", foreground="red")
        self.search_button.config(state="normal")

    def update_top_error(self, error_msg: str):
        """Mettre à jour en cas d'erreur Top 100"""
        self.top_status.config(text=f"❌ {error_msg}", foreground="red")
        self.top_button.config(state="normal")

    def clear_results(self):
        """Nettoyer l'arbre des résultats"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []

    def populate_tree(self):
        """Remplir l'arbre avec les résultats"""
        # Nettoyer seulement l'arbre, pas les résultats
        for item in self.tree.get_children():
            self.tree.delete(item)

        for result in self.results:
            name = result.get("name", "N/A")
            size = result.get("size", "N/A")
            seeders = str(result.get("seeders", 0))
            leechers = str(result.get("leechers", 0))
            source = f"{result.get('source_icon', '🔗')} {result.get('source_name', 'Unknown')}"

            # Couleur selon le nombre de seeders
            tags = []
            seeders_count = result.get("seeders", 0)
            if isinstance(seeders_count, (int, float)) and seeders_count > 50:
                tags = ["high_seeders"]
            elif isinstance(seeders_count, (int, float)) and seeders_count > 10:
                tags = ["medium_seeders"]
            else:
                tags = ["low_seeders"]

            self.tree.insert("", "end", values=(name, size, seeders, leechers, source), tags=tags)

        # Configuration des couleurs
        self.tree.tag_configure("high_seeders", foreground="#27ae60")  # Vert
        self.tree.tag_configure("medium_seeders", foreground="#f39c12")  # Orange
        self.tree.tag_configure("low_seeders", foreground="#e74c3c")   # Rouge

    def sort_by_column(self, column: str):
        """Trier par colonne"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Trier les résultats
        if column == "name":
            self.results.sort(key=lambda x: x.get("name", "").lower(), reverse=self.sort_reverse)
        elif column == "size":
            self.results.sort(key=lambda x: self._size_to_bytes(x.get("size", "")), reverse=self.sort_reverse)
        elif column == "seeders":
            self.results.sort(key=lambda x: int(x.get("seeders", 0)), reverse=self.sort_reverse)
        elif column == "leechers":
            self.results.sort(key=lambda x: int(x.get("leechers", 0)), reverse=self.sort_reverse)
        elif column == "source":
            self.results.sort(key=lambda x: x.get("source_name", ""), reverse=self.sort_reverse)

        # Mettre à jour l'affichage
        self.populate_tree()

        # Mettre à jour l'en-tête pour indiquer le tri
        for col in ["name", "size", "seeders", "leechers", "source"]:
            if col == column:
                arrow = " ▼" if self.sort_reverse else " ▲"
                current_text = self.tree.heading(col)["text"]
                new_text = current_text.split(" ")[0] + " " + current_text.split(" ")[1] + arrow
                self.tree.heading(col, text=new_text)
            else:
                # Remettre le texte original
                headers = {
                    "name": "📄 Nom",
                    "size": "💾 Taille",
                    "seeders": "🌱 Seeders",
                    "leechers": "📥 Leechers",
                    "source": "🌐 Source"
                }
                self.tree.heading(col, text=headers[col])

    def _size_to_bytes(self, size_str: str) -> int:
        """Convertir une taille en bytes pour le tri"""
        if not size_str or size_str == "N/A":
            return 0

        size_str = size_str.upper()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }

        for unit, multiplier in multipliers.items():
            if unit in size_str:
                try:
                    number = float(size_str.replace(unit, '').strip())
                    return int(number * multiplier)
                except ValueError:
                    return 0

        return 0

    def open_magnet(self, event):
        """Ouvrir le lien magnet au double-clic"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        index = self.tree.index(item)

        if index < len(self.results):
            result = self.results[index]
            magnet = result.get("magnet")

            if magnet:
                try:
                    webbrowser.open(magnet)
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'ouvrir le lien magnet: {e}")
            else:
                messagebox.showwarning("Attention", "Aucun lien magnet disponible")

    def run(self):
        """Lancer l'application"""
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    print("🏴‍☠️ TorrentHunt Desktop - Version Top 100")
    print("=" * 50)

    try:
        app = TorrentHuntGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'application")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")


if __name__ == "__main__":
    main()