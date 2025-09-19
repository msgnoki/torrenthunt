#!/usr/bin/env python3
"""
TorrentHunt Desktop - Modern Interface (Flathub Style)
Interface moderne avec thème sombre/clair et design épuré
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


class ModernTheme:
    """Gestionnaire de thèmes modernes"""

    DARK_THEME = {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'select_bg': '#404040',
        'select_fg': '#ffffff',
        'button_bg': '#3584e4',
        'button_fg': '#ffffff',
        'button_hover': '#2563c7',
        'accent': '#3584e4',
        'success': '#26a269',
        'warning': '#f6d32d',
        'error': '#e01b24',
        'card_bg': '#363636',
        'border': '#555555',
        'sidebar_bg': '#303030'
    }

    LIGHT_THEME = {
        'bg': '#fafafa',
        'fg': '#2e3436',
        'select_bg': '#e8f4f8',
        'select_fg': '#2e3436',
        'button_bg': '#3584e4',
        'button_fg': '#ffffff',
        'button_hover': '#2563c7',
        'accent': '#3584e4',
        'success': '#26a269',
        'warning': '#f57c00',
        'error': '#e01b24',
        'card_bg': '#ffffff',
        'border': '#d5d5d5',
        'sidebar_bg': '#f0f0f0'
    }

    def __init__(self, theme_name='dark'):
        self.current_theme = self.DARK_THEME if theme_name == 'dark' else self.LIGHT_THEME
        self.theme_name = theme_name

    def get(self, key):
        return self.current_theme.get(key, '#000000')


class TorrentHuntAPI:
    """Client API TorrentHunt optimisé"""

    def __init__(self):
        self.base_url = "https://torrent-api-py-nx0x.onrender.com"
        self.sites_info = {
            "piratebay": {"name": "The Pirate Bay", "icon": "🏴‍☠️", "color": "#e01b24"},
            "1337x": {"name": "1337x", "icon": "🔥", "color": "#f57c00"},
            "torrentgalaxy": {"name": "TorrentGalaxy", "icon": "🌌", "color": "#9141ac"},
            "rarbg": {"name": "RARBG", "icon": "💎", "color": "#3584e4"},
            "nyaa": {"name": "Nyaa", "icon": "🎌", "color": "#e01b24"},
            "yts": {"name": "YTS", "icon": "🎬", "color": "#26a269"},
            "eztv": {"name": "EZTV", "icon": "📺", "color": "#613583"}
        }

        self.categories = {
            "all": {"name": "All Content", "icon": "⭐", "desc": "All torrents"},
            "movies": {"name": "Movies", "icon": "🎬", "desc": "Films & Cinema"},
            "tv": {"name": "TV Shows", "icon": "📺", "desc": "Series & Episodes"},
            "music": {"name": "Music", "icon": "🎵", "desc": "Audio & Albums"},
            "books": {"name": "Books", "icon": "📚", "desc": "eBooks & Magazines"},
            "games": {"name": "Games", "icon": "🎮", "desc": "PC & Console Games"},
            "software": {"name": "Software", "icon": "💻", "desc": "Applications & Tools"},
            "anime": {"name": "Anime", "icon": "🎌", "desc": "Japanese Animation"}
        }

    async def create_session(self):
        """Créer une session HTTP optimisée"""
        headers = {
            'User-Agent': 'TorrentHunt-Desktop-Modern/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        }

        connector = aiohttp.TCPConnector(
            limit=20,
            limit_per_host=8,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30
        )

        timeout = aiohttp.ClientTimeout(total=25, connect=8)
        return aiohttp.ClientSession(
            connector=connector,
            headers=headers,
            timeout=timeout
        )

    async def search_torrents(self, query: str, sites: List[str], category: str = "all") -> List[Dict]:
        """Recherche avec gestion d'erreurs améliorée"""
        all_results = []
        session = await self.create_session()

        try:
            tasks = []
            for site in sites:
                task = self._search_site(session, site, query, category)
                tasks.append(task)

            # Exécution parallèle avec timeout
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for site_results in results:
                if isinstance(site_results, list):
                    all_results.extend(site_results)
                elif isinstance(site_results, Exception):
                    print(f"Erreur site: {site_results}")

        finally:
            await session.close()

        return all_results

    async def _search_site(self, session, site, query, category):
        """Recherche sur un site spécifique"""
        try:
            params = {"query": query, "site": site, "limit": 25}
            if category != "all":
                params["category"] = category

            url = f"{self.base_url}/api/v1/search"
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("data", [])

                    for result in results:
                        result["source_site"] = site
                        result["source_icon"] = self.sites_info.get(site, {}).get("icon", "🔗")
                        result["source_name"] = self.sites_info.get(site, {}).get("name", site)
                        result["source_color"] = self.sites_info.get(site, {}).get("color", "#666666")

                    return results
        except Exception as e:
            print(f"Erreur {site}: {e}")
            return []

    async def get_trending(self, sites: List[str], category: str = "all", limit: int = 50) -> List[Dict]:
        """Récupération des tendances"""
        all_results = []
        session = await self.create_session()

        try:
            tasks = []
            for site in sites:
                task = self._get_trending_site(session, site, limit//len(sites))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for site_results in results:
                if isinstance(site_results, list):
                    filtered = self._filter_by_category(site_results, category)
                    all_results.extend(filtered)

        finally:
            await session.close()

        return all_results

    async def _get_trending_site(self, session, site, limit):
        """Tendances d'un site spécifique"""
        try:
            params = {"site": site, "limit": limit}
            url = f"{self.base_url}/api/v1/trending"

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("data", [])

                    for result in results:
                        result["source_site"] = site
                        result["source_icon"] = self.sites_info.get(site, {}).get("icon", "🔗")
                        result["source_name"] = self.sites_info.get(site, {}).get("name", site)
                        result["source_color"] = self.sites_info.get(site, {}).get("color", "#666666")

                    return results
        except Exception as e:
            print(f"Erreur trending {site}: {e}")
            return []

    def _filter_by_category(self, results, category):
        """Filtrage intelligent par catégorie"""
        if category == "all":
            return results

        filtered = []
        for result in results:
            name = result.get("name", "").lower()
            torrent_cat = result.get("category", "").lower()

            if self._matches_category(name, torrent_cat, category):
                filtered.append(result)

        return filtered

    def _matches_category(self, name, torrent_category, target_category):
        """Logique de correspondance de catégorie"""
        keywords = {
            "movies": ["movie", "film", "cinema", "dvd", "bluray", "1080p", "720p", "4k"],
            "tv": ["s01", "s02", "s03", "season", "episode", "tv", "series", "hdtv"],
            "music": ["music", "audio", "mp3", "flac", "album", "song", "artist"],
            "books": ["book", "ebook", "pdf", "epub", "mobi", "magazine", "novel"],
            "games": ["game", "pc", "xbox", "playstation", "nintendo", "steam"],
            "software": ["software", "app", "program", "windows", "mac", "linux"],
            "anime": ["anime", "manga", "subbed", "dubbed", "japanese"]
        }

        target_keywords = keywords.get(target_category, [])
        return any(keyword in name or keyword in torrent_category for keyword in target_keywords)


class ModernTorrentGUI:
    """Interface moderne style Flathub"""

    def __init__(self):
        self.theme = ModernTheme('dark')
        self.api = TorrentHuntAPI()
        self.results = []
        self.sort_column = None
        self.sort_reverse = False

        self.setup_gui()
        self.apply_modern_style()

    def setup_gui(self):
        """Interface principale moderne"""
        self.root = tk.Tk()
        self.root.title("TorrentHunt - Modern")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.theme.get('bg'))

        # Style moderne
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Header moderne
        self.create_header()

        # Container principal avec sidebar
        self.create_main_container()

        # Sidebar navigation
        self.create_sidebar()

        # Zone de contenu
        self.create_content_area()

        # Footer avec status
        self.create_footer()

    def create_header(self):
        """Header moderne avec titre et contrôles"""
        header = tk.Frame(self.root, bg=self.theme.get('card_bg'), height=60)
        header.pack(fill="x", padx=20, pady=(20, 0))
        header.pack_propagate(False)

        # Logo et titre
        title_frame = tk.Frame(header, bg=self.theme.get('card_bg'))
        title_frame.pack(side="left", fill="y", pady=10)

        # Icône app
        app_icon = tk.Label(title_frame, text="🏴‍☠️", font=("Arial", 24),
                           bg=self.theme.get('card_bg'), fg=self.theme.get('accent'))
        app_icon.pack(side="left", padx=(10, 15))

        # Titre et sous-titre
        title_container = tk.Frame(title_frame, bg=self.theme.get('card_bg'))
        title_container.pack(side="left", fill="y")

        title_label = tk.Label(title_container, text="TorrentHunt",
                              font=("Arial", 18, "bold"),
                              bg=self.theme.get('card_bg'), fg=self.theme.get('fg'))
        title_label.pack(anchor="w")

        subtitle = tk.Label(title_container, text="Modern Torrent Search",
                           font=("Arial", 10),
                           bg=self.theme.get('card_bg'), fg=self.theme.get('fg'))
        subtitle.pack(anchor="w")

        # Contrôles header
        controls_frame = tk.Frame(header, bg=self.theme.get('card_bg'))
        controls_frame.pack(side="right", fill="y", pady=10, padx=10)

        # Toggle thème
        self.theme_button = tk.Button(controls_frame, text="🌙", font=("Arial", 16),
                                     command=self.toggle_theme,
                                     bg=self.theme.get('button_bg'), fg=self.theme.get('button_fg'),
                                     relief="flat", padx=15, pady=5)
        self.theme_button.pack(side="right", padx=5)

    def create_main_container(self):
        """Container principal avec layout moderne"""
        self.main_container = tk.Frame(self.root, bg=self.theme.get('bg'))
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

    def create_sidebar(self):
        """Sidebar de navigation moderne"""
        self.sidebar = tk.Frame(self.main_container, bg=self.theme.get('sidebar_bg'), width=280)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)

        # Section Search
        self.create_search_section()

        # Section Categories
        self.create_categories_section()

        # Section Sites
        self.create_sites_section()

    def create_search_section(self):
        """Section recherche dans la sidebar"""
        search_frame = tk.Frame(self.sidebar, bg=self.theme.get('sidebar_bg'))
        search_frame.pack(fill="x", padx=20, pady=20)

        # Titre section
        search_title = tk.Label(search_frame, text="🔍 Search",
                               font=("Arial", 14, "bold"),
                               bg=self.theme.get('sidebar_bg'), fg=self.theme.get('fg'))
        search_title.pack(anchor="w", pady=(0, 15))

        # Champ de recherche moderne
        search_container = tk.Frame(search_frame, bg=self.theme.get('card_bg'), relief="flat")
        search_container.pack(fill="x", pady=5)

        self.search_entry = tk.Entry(search_container, font=("Arial", 12),
                                    bg=self.theme.get('card_bg'), fg=self.theme.get('fg'),
                                    relief="flat", insertbackground=self.theme.get('fg'))
        self.search_entry.pack(fill="x", padx=15, pady=15)
        self.search_entry.bind("<Return>", lambda e: self.start_search())

        # Bouton de recherche moderne
        self.search_button = tk.Button(search_frame, text="Search Torrents",
                                      font=("Arial", 11, "bold"),
                                      command=self.start_search,
                                      bg=self.theme.get('accent'), fg=self.theme.get('button_fg'),
                                      relief="flat", pady=12)
        self.search_button.pack(fill="x", pady=(10, 0))

        # Bouton trending
        self.trending_button = tk.Button(search_frame, text="📈 View Trending",
                                        font=("Arial", 11),
                                        command=self.load_trending,
                                        bg=self.theme.get('card_bg'), fg=self.theme.get('fg'),
                                        relief="flat", pady=10)
        self.trending_button.pack(fill="x", pady=(5, 0))

    def create_categories_section(self):
        """Section catégories moderne"""
        cat_frame = tk.Frame(self.sidebar, bg=self.theme.get('sidebar_bg'))
        cat_frame.pack(fill="x", padx=20, pady=(20, 0))

        cat_title = tk.Label(cat_frame, text="📂 Categories",
                            font=("Arial", 14, "bold"),
                            bg=self.theme.get('sidebar_bg'), fg=self.theme.get('fg'))
        cat_title.pack(anchor="w", pady=(0, 15))

        # Container catégories
        self.cat_container = tk.Frame(cat_frame, bg=self.theme.get('sidebar_bg'))
        self.cat_container.pack(fill="x")

        self.category_var = tk.StringVar(value="all")

        for cat_key, cat_info in self.api.categories.items():
            cat_button = tk.Radiobutton(self.cat_container,
                                       text=f"{cat_info['icon']} {cat_info['name']}",
                                       variable=self.category_var, value=cat_key,
                                       font=("Arial", 10),
                                       bg=self.theme.get('sidebar_bg'), fg=self.theme.get('fg'),
                                       selectcolor=self.theme.get('accent'),
                                       relief="flat", anchor="w")
            cat_button.pack(fill="x", pady=2)

    def create_sites_section(self):
        """Section sites avec checkboxes modernes"""
        sites_frame = tk.Frame(self.sidebar, bg=self.theme.get('sidebar_bg'))
        sites_frame.pack(fill="x", padx=20, pady=(20, 0))

        sites_title = tk.Label(sites_frame, text="🌐 Torrent Sites",
                              font=("Arial", 14, "bold"),
                              bg=self.theme.get('sidebar_bg'), fg=self.theme.get('fg'))
        sites_title.pack(anchor="w", pady=(0, 15))

        # Sites container
        self.sites_container = tk.Frame(sites_frame, bg=self.theme.get('sidebar_bg'))
        self.sites_container.pack(fill="x")

        self.site_vars = {}
        for site_key, site_info in self.api.sites_info.items():
            var = tk.BooleanVar(value=True)
            self.site_vars[site_key] = var

            site_cb = tk.Checkbutton(self.sites_container,
                                    text=f"{site_info['icon']} {site_info['name']}",
                                    variable=var,
                                    font=("Arial", 10),
                                    bg=self.theme.get('sidebar_bg'), fg=self.theme.get('fg'),
                                    selectcolor=self.theme.get('accent'),
                                    relief="flat", anchor="w")
            site_cb.pack(fill="x", pady=2)

        # Boutons sélection
        btn_frame = tk.Frame(sites_frame, bg=self.theme.get('sidebar_bg'))
        btn_frame.pack(fill="x", pady=(15, 0))

        select_all_btn = tk.Button(btn_frame, text="Select All",
                                  font=("Arial", 9),
                                  command=lambda: self.toggle_all_sites(True),
                                  bg=self.theme.get('card_bg'), fg=self.theme.get('fg'),
                                  relief="flat", pady=8)
        select_all_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        select_none_btn = tk.Button(btn_frame, text="Select None",
                                   font=("Arial", 9),
                                   command=lambda: self.toggle_all_sites(False),
                                   bg=self.theme.get('card_bg'), fg=self.theme.get('fg'),
                                   relief="flat", pady=8)
        select_none_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def create_content_area(self):
        """Zone de contenu principale"""
        self.content_area = tk.Frame(self.main_container, bg=self.theme.get('bg'))
        self.content_area.pack(side="right", fill="both", expand=True)

        # Header de contenu
        content_header = tk.Frame(self.content_area, bg=self.theme.get('card_bg'), height=50)
        content_header.pack(fill="x", pady=(0, 15))
        content_header.pack_propagate(False)

        self.content_title = tk.Label(content_header, text="🚀 Ready to search",
                                     font=("Arial", 16, "bold"),
                                     bg=self.theme.get('card_bg'), fg=self.theme.get('fg'))
        self.content_title.pack(side="left", padx=20, pady=15)

        self.results_count = tk.Label(content_header, text="",
                                     font=("Arial", 11),
                                     bg=self.theme.get('card_bg'), fg=self.theme.get('fg'))
        self.results_count.pack(side="right", padx=20, pady=15)

        # Table des résultats
        self.create_results_table()

    def create_results_table(self):
        """Table de résultats moderne"""
        table_frame = tk.Frame(self.content_area, bg=self.theme.get('card_bg'))
        table_frame.pack(fill="both", expand=True)

        # Treeview avec style moderne
        columns = ("name", "size", "seeders", "leechers", "source")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        # Headers avec style
        self.tree.heading("name", text="📄 Name", command=lambda: self.sort_by_column("name"))
        self.tree.heading("size", text="💾 Size", command=lambda: self.sort_by_column("size"))
        self.tree.heading("seeders", text="🌱 Seeders", command=lambda: self.sort_by_column("seeders"))
        self.tree.heading("leechers", text="📥 Leechers", command=lambda: self.sort_by_column("leechers"))
        self.tree.heading("source", text="🌐 Source", command=lambda: self.sort_by_column("source"))

        # Largeurs colonnes
        self.tree.column("name", width=500, minwidth=300)
        self.tree.column("size", width=100, minwidth=80)
        self.tree.column("seeders", width=100, minwidth=70)
        self.tree.column("leechers", width=100, minwidth=70)
        self.tree.column("source", width=150, minwidth=120)

        # Scrollbars modernes
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        v_scroll.grid(row=0, column=1, sticky="ns", pady=20)
        h_scroll.grid(row=1, column=0, sticky="ew", padx=20)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Double-clic pour magnet
        self.tree.bind("<Double-1>", self.open_magnet)

    def create_footer(self):
        """Footer avec status et infos"""
        self.footer = tk.Frame(self.root, bg=self.theme.get('card_bg'), height=40)
        self.footer.pack(fill="x", padx=20, pady=(0, 20))
        self.footer.pack_propagate(False)

        self.status_label = tk.Label(self.footer, text="Ready",
                                    font=("Arial", 10),
                                    bg=self.theme.get('card_bg'), fg=self.theme.get('success'))
        self.status_label.pack(side="left", padx=20, pady=10)

        # Info API
        api_info = tk.Label(self.footer, text="API: torrent-api-py-nx0x.onrender.com",
                           font=("Arial", 9),
                           bg=self.theme.get('card_bg'), fg=self.theme.get('fg'))
        api_info.pack(side="right", padx=20, pady=10)

    def apply_modern_style(self):
        """Application du style moderne"""
        # Style TTK personnalisé
        self.style.configure('Modern.Treeview',
                           background=self.theme.get('card_bg'),
                           foreground=self.theme.get('fg'),
                           fieldbackground=self.theme.get('card_bg'),
                           borderwidth=0)

        self.style.configure('Modern.Treeview.Heading',
                           background=self.theme.get('sidebar_bg'),
                           foreground=self.theme.get('fg'),
                           borderwidth=1,
                           relief='flat')

        self.tree.configure(style='Modern.Treeview')

    def toggle_theme(self):
        """Basculer entre thème clair/sombre"""
        new_theme = 'light' if self.theme.theme_name == 'dark' else 'dark'
        self.theme = ModernTheme(new_theme)

        # Mettre à jour l'icône du bouton
        self.theme_button.config(text="☀️" if new_theme == 'dark' else "🌙")

        # Recharger l'interface avec le nouveau thème
        self.refresh_theme()

    def refresh_theme(self):
        """Actualiser les couleurs avec le nouveau thème"""
        # Mettre à jour tous les widgets avec les nouvelles couleurs
        widgets_to_update = [
            (self.root, {'bg': self.theme.get('bg')}),
            # Ajouter d'autres widgets selon les besoins
        ]

        for widget, config in widgets_to_update:
            widget.configure(**config)

        self.apply_modern_style()

    def toggle_all_sites(self, select_all: bool):
        """Sélectionner/désélectionner tous les sites"""
        for var in self.site_vars.values():
            var.set(select_all)

    def get_selected_sites(self) -> List[str]:
        """Obtenir la liste des sites sélectionnés"""
        return [site for site, var in self.site_vars.items() if var.get()]

    def start_search(self):
        """Démarrer une recherche"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term")
            return

        selected_sites = self.get_selected_sites()
        if not selected_sites:
            messagebox.showwarning("Warning", "Please select at least one site")
            return

        category = self.category_var.get()

        self.search_button.config(state="disabled", text="Searching...")
        self.status_label.config(text="🔍 Searching torrents...", fg=self.theme.get('warning'))
        self.content_title.config(text=f"🔍 Searching: {query}")

        # Nettoyer les résultats précédents
        self.clear_results()

        # Lancer la recherche en arrière-plan
        thread = threading.Thread(target=self.search_thread, args=(query, selected_sites, category))
        thread.daemon = True
        thread.start()

    def load_trending(self):
        """Charger les tendances"""
        selected_sites = self.get_selected_sites()
        if not selected_sites:
            messagebox.showwarning("Warning", "Please select at least one site")
            return

        category = self.category_var.get()

        self.trending_button.config(state="disabled", text="Loading...")
        self.status_label.config(text="📈 Loading trending...", fg=self.theme.get('warning'))
        self.content_title.config(text="📈 Trending Torrents")

        # Nettoyer les résultats précédents
        self.clear_results()

        # Lancer le chargement en arrière-plan
        thread = threading.Thread(target=self.trending_thread, args=(selected_sites, category))
        thread.daemon = True
        thread.start()

    def search_thread(self, query: str, sites: List[str], category: str):
        """Thread de recherche"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(self.api.search_torrents(query, sites, category))
            self.root.after(0, self.update_results, results, "search")

        except Exception as e:
            error_msg = f"Search error: {e}"
            self.root.after(0, self.update_error, error_msg, "search")
        finally:
            loop.close()

    def trending_thread(self, sites: List[str], category: str):
        """Thread des tendances"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(self.api.get_trending(sites, category))
            self.root.after(0, self.update_results, results, "trending")

        except Exception as e:
            error_msg = f"Trending error: {e}"
            self.root.after(0, self.update_error, error_msg, "trending")
        finally:
            loop.close()

    def update_results(self, results: List[Dict], mode: str):
        """Mettre à jour les résultats"""
        self.results = results
        self.populate_tree()

        count = len(results)
        self.results_count.config(text=f"{count} torrents found")
        self.status_label.config(text=f"✅ Found {count} torrents", fg=self.theme.get('success'))

        if mode == "search":
            self.search_button.config(state="normal", text="Search Torrents")
        else:
            self.trending_button.config(state="normal", text="📈 View Trending")

    def update_error(self, error_msg: str, mode: str):
        """Mettre à jour en cas d'erreur"""
        self.status_label.config(text=f"❌ {error_msg}", fg=self.theme.get('error'))

        if mode == "search":
            self.search_button.config(state="normal", text="Search Torrents")
        else:
            self.trending_button.config(state="normal", text="📈 View Trending")

    def clear_results(self):
        """Nettoyer l'arbre des résultats"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []
        self.results_count.config(text="")

    def populate_tree(self):
        """Remplir l'arbre avec les résultats"""
        # Nettoyer seulement l'arbre
        for item in self.tree.get_children():
            self.tree.delete(item)

        for result in self.results:
            name = result.get("name", "N/A")
            size = result.get("size", "N/A")
            seeders = str(result.get("seeders", 0))
            leechers = str(result.get("leechers", 0))
            source = f"{result.get('source_icon', '🔗')} {result.get('source_name', 'Unknown')}"

            # Tags pour couleur selon seeders
            tags = []
            seeders_count = result.get("seeders", 0)
            if isinstance(seeders_count, (int, float)):
                if seeders_count > 100:
                    tags = ["excellent"]
                elif seeders_count > 50:
                    tags = ["good"]
                elif seeders_count > 10:
                    tags = ["average"]
                else:
                    tags = ["poor"]

            self.tree.insert("", "end", values=(name, size, seeders, leechers, source), tags=tags)

        # Configuration des couleurs selon les seeders
        self.tree.tag_configure("excellent", foreground=self.theme.get('success'))
        self.tree.tag_configure("good", foreground="#26a269")
        self.tree.tag_configure("average", foreground=self.theme.get('warning'))
        self.tree.tag_configure("poor", foreground=self.theme.get('error'))

    def sort_by_column(self, column: str):
        """Trier par colonne"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Logique de tri
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

        self.populate_tree()

    def _size_to_bytes(self, size_str: str) -> int:
        """Convertir taille en bytes pour tri"""
        if not size_str or size_str == "N/A":
            return 0

        size_str = size_str.upper()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}

        for unit, multiplier in multipliers.items():
            if unit in size_str:
                try:
                    number = float(size_str.replace(unit, '').strip())
                    return int(number * multiplier)
                except ValueError:
                    return 0
        return 0

    def open_magnet(self, event):
        """Ouvrir le lien magnet"""
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
                    self.status_label.config(text="🔗 Magnet link opened", fg=self.theme.get('success'))
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open magnet link: {e}")
            else:
                messagebox.showwarning("Warning", "No magnet link available")

    def run(self):
        """Lancer l'application"""
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    print("🏴‍☠️ TorrentHunt Desktop - Modern Interface")
    print("=" * 60)
    print("🎨 Modern Flathub-style interface")
    print("🌙 Dark/Light theme support")
    print("⚡ Optimized for Linux desktop")
    print("=" * 60)

    try:
        app = ModernTorrentGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()