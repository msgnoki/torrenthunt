#!/usr/bin/env python3
"""
TorrentHunt Desktop - Version améliorée avec tri et sélection de sites
Fonctionnalités: tri des colonnes + cases à cocher pour sites
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
        self.sites_info = {
            "piratebay": {"name": "ThePirateBay", "icon": "🏴‍☠️", "color": "#e74c3c"},
            "1337x": {"name": "1337x", "icon": "🔥", "color": "#f39c12"},
            "torrentgalaxy": {"name": "TorrentGalaxy", "icon": "🌌", "color": "#9b59b6"},
            "rarbg": {"name": "RARBG", "icon": "💎", "color": "#3498db"},
            "nyaa": {"name": "Nyaa", "icon": "🎌", "color": "#e91e63"},
            "yts": {"name": "YTS", "icon": "🎬", "color": "#2ecc71"},
            "eztv": {"name": "EZTV", "icon": "📺", "color": "#34495e"}
        }

    async def create_session(self):
        """Créer une session HTTP"""
        if not self.session:
            headers = {
                'User-Agent': 'TorrentHunt Desktop Enhanced/1.0',
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

    async def search_selected_sites(self, query: str, selected_sites: List[str]) -> List[Dict]:
        """Rechercher seulement sur les sites sélectionnés"""
        await self.create_session()

        # Lancer les recherches en parallèle pour les sites sélectionnés
        tasks = []
        for site in selected_sites:
            task = self.search_site(query, site)
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_torrents = []
            for i, site_results in enumerate(results):
                if isinstance(site_results, list):
                    all_torrents.extend(site_results)
                    print(f"✓ {selected_sites[i]}: {len(site_results)} résultats")
                elif isinstance(site_results, Exception):
                    print(f"✗ {selected_sites[i]}: {site_results}")

            print(f"Total: {len(all_torrents)} torrents trouvés")
            return all_torrents

        except Exception as e:
            print(f"Erreur recherche globale: {e}")
            return []


class SortableTreeview(ttk.Treeview):
    """Treeview avec tri des colonnes"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.sort_columns = {}  # Track sort direction for each column

    def heading(self, column, **kwargs):
        """Override heading to add sorting functionality"""
        if "command" not in kwargs:
            # Add sort command to column header
            kwargs["command"] = lambda c=column: self.sort_by_column(c)
        super().heading(column, **kwargs)

    def sort_by_column(self, column):
        """Sort treeview contents by column"""
        # Determine sort direction
        reverse = self.sort_columns.get(column, False)
        self.sort_columns[column] = not reverse

        # Get all items with their values
        items = [(self.item(child)["values"], child) for child in self.get_children("")]

        # Sort items based on column
        column_index = list(self["columns"]).index(column)

        try:
            # Try numeric sort for numbers (seeders, leechers)
            if column in ["seeders", "leechers"]:
                items.sort(key=lambda x: int(str(x[0][column_index]).replace(",", "")) if x[0][column_index] else 0, reverse=reverse)
            else:
                # String sort for other columns
                items.sort(key=lambda x: str(x[0][column_index]).lower(), reverse=reverse)
        except (ValueError, IndexError):
            # Fallback to string sort
            items.sort(key=lambda x: str(x[0][column_index]).lower(), reverse=reverse)

        # Reorder items in treeview
        for index, (values, child) in enumerate(items):
            self.move(child, "", index)

        # Update column heading to show sort direction
        direction = " ↓" if reverse else " ↑"
        current_text = self.heading(column)["text"]
        if current_text:
            # Remove existing arrows
            clean_text = current_text.replace(" ↑", "").replace(" ↓", "")
            self.heading(column, text=clean_text + direction)


class TorrentHuntGUI:
    """Interface graphique TorrentHunt Desktop avec tri et sélection de sites"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏴‍☠️ TorrentHunt Desktop Enhanced - Tri & Sélection")
        self.root.geometry("1500x900")
        self.root.minsize(1200, 700)

        # Style
        self.setup_styles()

        # API client
        self.api = TorrentHuntAPI()
        self.current_results = []

        # Variables pour sélection des sites
        self.site_vars = {}
        for site in self.api.sites_info.keys():
            self.site_vars[site] = tk.BooleanVar(value=True)  # Tous sélectionnés par défaut

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
        style.configure('Treeview', rowheight=30, font=('Arial', 9))
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
        main_frame.rowconfigure(3, weight=1)

        # En-tête
        self.create_header(main_frame)

        # Frame de recherche
        self.create_search_frame(main_frame)

        # Frame de sélection des sites
        self.create_sites_frame(main_frame)

        # Frame des résultats
        self.create_results_frame(main_frame)

        # Status bar
        self.create_status_bar(main_frame)

    def create_header(self, parent):
        """Créer l'en-tête"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(header_frame, text="🏴‍☠️ TorrentHunt Desktop Enhanced", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(header_frame, text="Tri des colonnes • Sélection de sites • API Officielle",
                                 font=('Arial', 10, 'italic'), foreground='#95a5a6')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

    def create_search_frame(self, parent):
        """Créer le frame de recherche"""
        search_frame = ttk.LabelFrame(parent, text="🔍 Recherche Torrent", padding="15")
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
        search_btn = ttk.Button(search_frame, text="🚀 Rechercher sur sites sélectionnés",
                               command=self.search_torrents)
        search_btn.grid(row=0, column=2)

        # Barre de progression
        progress_frame = ttk.Frame(search_frame)
        progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def create_sites_frame(self, parent):
        """Créer le frame de sélection des sites"""
        sites_frame = ttk.LabelFrame(parent, text="🌐 Sélection des Sites Torrent", padding="10")
        sites_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Frame avec colonnes pour les checkboxes
        checkboxes_frame = ttk.Frame(sites_frame)
        checkboxes_frame.pack(fill=tk.X)

        # Boutons de sélection rapide
        controls_frame = ttk.Frame(sites_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))

        select_all_btn = ttk.Button(controls_frame, text="✅ Tout sélectionner",
                                   command=self.select_all_sites)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))

        select_none_btn = ttk.Button(controls_frame, text="❌ Tout désélectionner",
                                    command=self.select_no_sites)
        select_none_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Status de sélection
        self.selection_status = ttk.Label(controls_frame, text="", style='Stats.TLabel')
        self.selection_status.pack(side=tk.RIGHT)

        # Créer les checkboxes pour chaque site
        col = 0
        for site, info in self.api.sites_info.items():
            checkbox = ttk.Checkbutton(
                checkboxes_frame,
                text=f"{info['icon']} {info['name']}",
                variable=self.site_vars[site],
                command=self.update_selection_status
            )
            checkbox.grid(row=0, column=col, sticky=tk.W, padx=(0, 20), pady=5)
            col += 1

        # Mettre à jour le status initial
        self.update_selection_status()

    def create_results_frame(self, parent):
        """Créer le frame des résultats avec tri"""
        results_frame = ttk.LabelFrame(parent, text="📊 Résultats (cliquez sur les en-têtes pour trier ↕️)", padding="5")
        results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Treeview avec tri
        columns = ('name', 'site', 'size', 'seeders', 'leechers', 'date')
        self.tree = SortableTreeview(results_frame, columns=columns, show='headings', height=18)

        # Configuration des colonnes
        self.tree.heading('name', text='📁 Nom du torrent')
        self.tree.heading('site', text='🌐 Site')
        self.tree.heading('size', text='💾 Taille')
        self.tree.heading('seeders', text='🔼 Seeders')
        self.tree.heading('leechers', text='🔽 Leechers')
        self.tree.heading('date', text='📅 Date')

        # Largeurs des colonnes
        self.tree.column('name', width=500, anchor=tk.W)
        self.tree.column('site', width=140, anchor=tk.CENTER)
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

    def create_status_bar(self, parent):
        """Créer la barre de statut"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
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

    def select_all_sites(self):
        """Sélectionner tous les sites"""
        for var in self.site_vars.values():
            var.set(True)
        self.update_selection_status()

    def select_no_sites(self):
        """Désélectionner tous les sites"""
        for var in self.site_vars.values():
            var.set(False)
        self.update_selection_status()

    def update_selection_status(self):
        """Mettre à jour le statut de sélection"""
        selected = [site for site, var in self.site_vars.items() if var.get()]
        total = len(self.site_vars)
        selected_count = len(selected)

        if selected_count == 0:
            self.selection_status.config(text="❌ Aucun site sélectionné", foreground='#e74c3c')
        elif selected_count == total:
            self.selection_status.config(text=f"✅ Tous les sites sélectionnés ({selected_count})", foreground='#27ae60')
        else:
            self.selection_status.config(text=f"🎯 {selected_count}/{total} sites sélectionnés", foreground='#f39c12')

    def get_selected_sites(self):
        """Obtenir la liste des sites sélectionnés"""
        return [site for site, var in self.site_vars.items() if var.get()]

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

        # Vérifier qu'au moins un site est sélectionné
        selected_sites = self.get_selected_sites()
        if not selected_sites:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un site de torrent")
            return

        # Nettoyer les résultats précédents
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Démarrer la recherche dans un thread
        thread = threading.Thread(target=self.run_search, args=(query, selected_sites))
        thread.daemon = True
        thread.start()

    def run_search(self, query: str, selected_sites: List[str]):
        """Exécuter la recherche dans un thread séparé"""
        self.root.after(0, self.start_progress)
        sites_names = [self.api.sites_info[site]["name"] for site in selected_sites]
        sites_text = ", ".join(sites_names[:3]) + (f" +{len(sites_names)-3}" if len(sites_names) > 3 else "")
        self.root.after(0, lambda: self.status_var.set(f"🔍 Recherche '{query}' sur {sites_text}..."))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            start_time = time.time()
            results = loop.run_until_complete(self.api.search_selected_sites(query, selected_sites))
            end_time = time.time()

            search_time = end_time - start_time
            self.root.after(0, lambda: self.display_results(results, query, search_time, selected_sites))

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

    def display_results(self, results: List[Dict], query: str, search_time: float, selected_sites: List[str]):
        """Afficher les résultats"""
        self.current_results = results

        if not results:
            self.status_var.set("❌ Aucun résultat trouvé")
            sites_names = [self.api.sites_info[site]["name"] for site in selected_sites]
            messagebox.showinfo("Aucun résultat",
                              f"Aucun torrent trouvé pour '{query}' sur:\n{', '.join(sites_names)}\n\n" +
                              "Suggestions:\n" +
                              "• Vérifiez l'orthographe\n" +
                              "• Essayez des termes plus génériques\n" +
                              "• Sélectionnez plus de sites\n" +
                              "• Utilisez des mots-clés en anglais")
            return

        # Trier par seeders par défaut (décroissant)
        results.sort(key=lambda x: x.get('seeders', 0), reverse=True)

        # Compter par site
        sites_count = {}
        for result in results:
            site = result['site']
            sites_count[site] = sites_count.get(site, 0) + 1

        # Ajouter les résultats au treeview
        for i, result in enumerate(results):
            site_info = self.api.sites_info.get(result['site'], {"icon": "🌐", "name": result['site']})
            site_icon = site_info["icon"]

            # Couleurs alternées
            tags = ('oddrow',) if i % 2 == 0 else ('evenrow',)

            values = (
                result['name'][:85] + ('...' if len(result['name']) > 85 else ''),
                f"{site_icon} {site_info['name']}",
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
        sites_info = " • ".join([f"{self.api.sites_info[site]['name']}: {count}" for site, count in sites_count.items()])

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
        print("🏴‍☠️ Lancement de TorrentHunt Desktop Enhanced...")
        print("✨ Fonctionnalités: Tri des colonnes + Sélection des sites")
        print("🌐 API: https://torrent-api-py-nx0x.onrender.com")

        app = TorrentHuntGUI()
        app.run()

    except Exception as e:
        print(f"Erreur fatale: {e}")
        messagebox.showerror("Erreur", f"Impossible de lancer l'application:\n{e}")


if __name__ == "__main__":
    main()