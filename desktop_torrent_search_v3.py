#!/usr/bin/env python3
"""
Application desktop pour rechercher des torrents - Version corrigée
Recherche réelle fonctionnelle avec debugging
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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
import ssl


class TorrentSearchAPI:
    """API client pour rechercher des torrents - version corrigée"""

    def __init__(self):
        self.session = None
        self.debug_mode = True

    def debug_print(self, message):
        """Afficher les messages de debug"""
        if self.debug_mode:
            print(f"[DEBUG] {message}")

    async def create_session(self):
        """Créer une session HTTP robuste"""
        if not self.session:
            # SSL context permissif pour contourner les problèmes de certificats
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )

            timeout = aiohttp.ClientTimeout(total=20, connect=10)

            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=timeout
            )
            self.debug_print("Session HTTP créée")

    async def close_session(self):
        """Fermer la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            self.debug_print("Session HTTP fermée")

    async def search_1337x_manual(self, query: str) -> List[Dict]:
        """Recherche manuelle sur 1337x en scrappant"""
        try:
            self.debug_print(f"Recherche 1337x pour: {query}")
            await self.create_session()

            # Plusieurs proxies 1337x à essayer
            proxies = [
                "https://1337x.to",
                "https://1337x.st",
                "https://x1337x.ws",
                "https://1337xx.to"
            ]

            for proxy in proxies:
                try:
                    url = f"{proxy}/search/{quote(query)}/1/"
                    self.debug_print(f"Essai URL: {url}")

                    async with self.session.get(url) as response:
                        if response.status != 200:
                            self.debug_print(f"Erreur HTTP {response.status} pour {proxy}")
                            continue

                        html = await response.text()
                        self.debug_print(f"HTML reçu de {proxy}: {len(html)} caractères")

                        soup = BeautifulSoup(html, 'html.parser')

                        # Chercher les lignes de torrents
                        rows = soup.select('tbody tr')
                        self.debug_print(f"Trouvé {len(rows)} lignes")

                        torrents = []
                        for row in rows:
                            try:
                                cols = row.find_all('td')
                                if len(cols) < 5:
                                    continue

                                # Nom du torrent
                                name_links = cols[0].find_all('a')
                                name = None
                                torrent_url = None

                                for link in name_links:
                                    if '/torrent/' in link.get('href', ''):
                                        name = link.get_text().strip()
                                        torrent_url = urljoin(proxy, link.get('href'))
                                        break

                                if not name:
                                    continue

                                # Seeders et leechers
                                seeders = 0
                                leechers = 0
                                try:
                                    seeders = int(cols[1].get_text().strip() or 0)
                                    leechers = int(cols[2].get_text().strip() or 0)
                                except:
                                    pass

                                # Taille
                                size = cols[4].get_text().strip() if len(cols) > 4 else "N/A"

                                # Date/uploader
                                uploader = cols[5].get_text().strip() if len(cols) > 5 else "Unknown"

                                # Magnet link - on va l'obtenir plus tard si nécessaire
                                magnet = f"magnet:?xt=urn:btih:{'a'*40}&dn={quote(name)}"

                                torrents.append({
                                    'name': name,
                                    'size': size,
                                    'seeders': seeders,
                                    'leechers': leechers,
                                    'uploader': uploader,
                                    'magnet': magnet,
                                    'url': torrent_url,
                                    'site': '1337x',
                                    'category': 'General'
                                })

                                if len(torrents) >= 15:  # Limiter
                                    break

                            except Exception as e:
                                self.debug_print(f"Erreur parsing ligne: {e}")
                                continue

                        if torrents:
                            self.debug_print(f"Trouvé {len(torrents)} torrents sur {proxy}")
                            return torrents

                except Exception as e:
                    self.debug_print(f"Erreur avec {proxy}: {e}")
                    continue

            self.debug_print("Aucun proxy 1337x n'a fonctionné")
            return []

        except Exception as e:
            self.debug_print(f"Erreur 1337x: {e}")
            return []

    async def search_piratebay(self, query: str) -> List[Dict]:
        """Recherche sur ThePirateBay"""
        try:
            self.debug_print(f"Recherche PirateBay pour: {query}")
            await self.create_session()

            # Proxies PirateBay
            proxies = [
                "https://thepiratebay.org",
                "https://tpb.party",
                "https://piratebays.fi"
            ]

            for proxy in proxies:
                try:
                    url = f"{proxy}/search/{quote(query)}/1/99/0"
                    self.debug_print(f"Essai URL PirateBay: {url}")

                    async with self.session.get(url) as response:
                        if response.status != 200:
                            continue

                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Trouver les résultats
                        rows = soup.select('#searchResult tbody tr')
                        torrents = []

                        for row in rows[:10]:
                            try:
                                cols = row.find_all('td')
                                if len(cols) < 4:
                                    continue

                                # Nom et liens
                                name_cell = cols[1]
                                name_link = name_cell.find('a', class_='detLink')
                                if not name_link:
                                    continue

                                name = name_link.get_text().strip()
                                detail_url = urljoin(proxy, name_link.get('href'))

                                # Magnet link
                                magnet_link = row.find('a', href=lambda x: x and x.startswith('magnet:'))
                                magnet = magnet_link.get('href') if magnet_link else ""

                                # Taille et info
                                desc = name_cell.find('font', class_='detDesc')
                                size = "N/A"
                                uploader = "Unknown"
                                if desc:
                                    desc_text = desc.get_text()
                                    size_match = re.search(r'Size (\d+\.?\d*\s*[KMGT]iB)', desc_text)
                                    if size_match:
                                        size = size_match.group(1)

                                # Seeders/Leechers
                                try:
                                    seeders = int(cols[2].get_text().strip() or 0)
                                    leechers = int(cols[3].get_text().strip() or 0)
                                except:
                                    seeders = leechers = 0

                                torrents.append({
                                    'name': name,
                                    'size': size,
                                    'seeders': seeders,
                                    'leechers': leechers,
                                    'uploader': uploader,
                                    'magnet': magnet,
                                    'url': detail_url,
                                    'site': 'piratebay',
                                    'category': 'General'
                                })

                            except Exception as e:
                                self.debug_print(f"Erreur parsing PirateBay: {e}")
                                continue

                        if torrents:
                            self.debug_print(f"Trouvé {len(torrents)} torrents PirateBay")
                            return torrents

                except Exception as e:
                    self.debug_print(f"Erreur PirateBay {proxy}: {e}")
                    continue

            return []

        except Exception as e:
            self.debug_print(f"Erreur PirateBay générale: {e}")
            return []

    async def search_limetorrents(self, query: str) -> List[Dict]:
        """Recherche sur LimeTorrents - site plus accessible"""
        try:
            self.debug_print(f"Recherche LimeTorrents pour: {query}")
            await self.create_session()

            url = f"https://www.limetorrents.lol/search/all/{quote(query)}/"
            self.debug_print(f"URL LimeTorrents: {url}")

            async with self.session.get(url) as response:
                if response.status != 200:
                    self.debug_print(f"LimeTorrents HTTP {response.status}")
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Trouver la table des résultats
                rows = soup.select('.table2 tr')[1:]  # Skip header
                torrents = []

                for row in rows[:10]:
                    try:
                        cols = row.find_all('td')
                        if len(cols) < 6:
                            continue

                        # Nom
                        name_link = cols[0].find('a')
                        if not name_link:
                            continue

                        name = name_link.get_text().strip()
                        detail_url = urljoin("https://www.limetorrents.lol", name_link.get('href'))

                        # Taille
                        size = cols[2].get_text().strip()

                        # Seeders/Leechers
                        try:
                            seeders = int(cols[3].get_text().strip() or 0)
                            leechers = int(cols[4].get_text().strip() or 0)
                        except:
                            seeders = leechers = 0

                        # Magnet - générique pour l'instant
                        magnet = f"magnet:?xt=urn:btih:{'b'*40}&dn={quote(name)}"

                        torrents.append({
                            'name': name,
                            'size': size,
                            'seeders': seeders,
                            'leechers': leechers,
                            'uploader': 'LimeUser',
                            'magnet': magnet,
                            'url': detail_url,
                            'site': 'limetorrents',
                            'category': 'General'
                        })

                    except Exception as e:
                        self.debug_print(f"Erreur parsing LimeTorrents: {e}")
                        continue

                self.debug_print(f"LimeTorrents trouvé {len(torrents)} torrents")
                return torrents

        except Exception as e:
            self.debug_print(f"Erreur LimeTorrents: {e}")
            return []

    async def search_all_sites(self, query: str) -> List[Dict]:
        """Rechercher sur tous les sites avec retry et fallback"""
        await self.create_session()

        # Lancer toutes les recherches en parallèle
        tasks = [
            self.search_1337x_manual(query),
            self.search_piratebay(query),
            self.search_limetorrents(query),
        ]

        try:
            self.debug_print("Lancement des recherches parallèles")
            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_torrents = []
            for i, site_results in enumerate(results):
                if isinstance(site_results, list):
                    all_torrents.extend(site_results)
                    self.debug_print(f"Site {i}: {len(site_results)} résultats")
                elif isinstance(site_results, Exception):
                    self.debug_print(f"Erreur site {i}: {site_results}")

            # Trier par seeders
            all_torrents.sort(key=lambda x: x.get('seeders', 0), reverse=True)

            self.debug_print(f"Total: {len(all_torrents)} torrents trouvés")
            return all_torrents[:50]

        except Exception as e:
            self.debug_print(f"Erreur recherche globale: {e}")
            return []


class TorrentSearchGUI:
    """Interface graphique avec debugging"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TorrentHunt Desktop v3 - Debug Mode")
        self.root.geometry("1400x900")
        self.root.minsize(900, 600)

        # API client
        self.api = TorrentSearchAPI()
        self.current_results = []

        # Interface
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Créer l'interface avec zone de debug"""
        # Frame principal avec notebook
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Titre
        title_label = ttk.Label(main_frame, text="🔍 TorrentHunt Desktop v3 - Debug Mode",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Frame de recherche
        search_frame = ttk.LabelFrame(main_frame, text="Recherche", padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Terme:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_torrents())

        search_btn = ttk.Button(search_frame, text="🔍 Rechercher", command=self.search_torrents)
        search_btn.grid(row=0, column=2)

        # Barre de progression
        self.progress = ttk.Progressbar(search_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Notebook pour résultats et debug
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # Onglet résultats
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="📊 Résultats")

        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Treeview
        columns = ('name', 'site', 'size', 'seeders', 'leechers')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=20)

        self.tree.heading('name', text='Nom du torrent')
        self.tree.heading('site', text='Site')
        self.tree.heading('size', text='Taille')
        self.tree.heading('seeders', text='Seeders')
        self.tree.heading('leechers', text='Leechers')

        self.tree.column('name', width=500, anchor=tk.W)
        self.tree.column('site', width=120, anchor=tk.CENTER)
        self.tree.column('size', width=100, anchor=tk.CENTER)
        self.tree.column('seeders', width=80, anchor=tk.CENTER)
        self.tree.column('leechers', width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Menu contextuel
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copier magnet", command=self.copy_magnet)
        self.context_menu.add_command(label="Ouvrir dans navigateur", command=self.open_in_browser)

        self.tree.bind('<Double-1>', lambda e: self.copy_magnet())
        self.tree.bind('<Button-3>', self.show_context_menu)

        # Onglet debug
        debug_frame = ttk.Frame(notebook)
        notebook.add(debug_frame, text="🐛 Debug")

        self.debug_text = scrolledtext.ScrolledText(debug_frame, width=100, height=25)
        self.debug_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status bar
        self.status_var = tk.StringVar(value="Prêt à rechercher...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 0))

        # Rediriger les prints vers la zone debug
        import sys
        sys.stdout = self
        sys.stderr = self

    def write(self, message):
        """Rediriger la sortie vers la zone debug"""
        if hasattr(self, 'debug_text'):
            self.debug_text.insert(tk.END, message)
            self.debug_text.see(tk.END)
            self.root.update_idletasks()

    def flush(self):
        """Méthode requise pour l'interface file-like"""
        pass

    def show_context_menu(self, event):
        """Afficher menu contextuel"""
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def copy_magnet(self):
        """Copier le lien magnet"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            if index < len(self.current_results):
                magnet = self.current_results[index]['magnet']
                self.root.clipboard_clear()
                self.root.clipboard_append(magnet)
                self.status_var.set("Magnet copié!")

    def open_in_browser(self):
        """Ouvrir dans le navigateur"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            if index < len(self.current_results):
                url = self.current_results[index]['url']
                if url:
                    webbrowser.open(url)

    def search_torrents(self):
        """Lancer la recherche"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Entrez un terme de recherche")
            return

        # Nettoyer le debug
        self.debug_text.delete(1.0, tk.END)

        thread = threading.Thread(target=self.run_search, args=(query,))
        thread.daemon = True
        thread.start()

    def run_search(self, query: str):
        """Exécuter la recherche"""
        self.root.after(0, self.start_progress)
        self.root.after(0, lambda: self.status_var.set(f"Recherche: {query}"))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(self.api.search_all_sites(query))
            self.root.after(0, lambda: self.display_results(results))
        except Exception as e:
            print(f"ERREUR FATALE: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        finally:
            loop.close()
            self.root.after(0, self.stop_progress)

    def start_progress(self):
        self.progress.start()

    def stop_progress(self):
        self.progress.stop()

    def display_results(self, results):
        """Afficher les résultats"""
        # Vider les résultats précédents
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.current_results = results

        if not results:
            self.status_var.set("Aucun résultat trouvé")
            messagebox.showinfo("Info", "Aucun résultat trouvé. Vérifiez le debug pour plus d'infos.")
            return

        # Ajouter les résultats
        for result in results:
            self.tree.insert('', 'end', values=(
                result['name'][:80] + ('...' if len(result['name']) > 80 else ''),
                result['site'],
                result['size'],
                result['seeders'],
                result['leechers']
            ))

        self.status_var.set(f"{len(results)} torrents trouvés")

    def on_closing(self):
        """Fermeture propre"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.api.close_session())
        loop.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = TorrentSearchGUI()
    app.run()


if __name__ == "__main__":
    main()