package ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import data.models.*
import ui.components.*
import ui.viewmodels.TorrentViewModel

/**
 * Main Screen with sidebar navigation and content area
 * Implements the same layout as our Python Flathub-style version
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen() {
    val viewModel = remember { TorrentViewModel() }

    val searchResults by viewModel.searchResults.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val selectedSites by viewModel.selectedSites.collectAsState()
    val selectedCategory by viewModel.selectedCategory.collectAsState()
    val currentMode by viewModel.currentMode.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        // Top App Bar
        TopAppBar(
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("🏴‍☠️", style = MaterialTheme.typography.headlineMedium)
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            "TorrentHunt",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            "Modern Torrent Search",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            },
            actions = {
                // Theme toggle button
                IconButton(
                    onClick = { /* TODO: Implement theme toggle */ }
                ) {
                    Icon(Icons.Default.DarkMode, "Toggle theme")
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        )

        Row(modifier = Modifier.fillMaxSize()) {
            // Sidebar
            SidebarPanel(
                selectedSites = selectedSites,
                selectedCategory = selectedCategory,
                currentMode = currentMode,
                onSitesChanged = { viewModel.updateSelectedSites(it) },
                onCategoryChanged = { viewModel.updateSelectedCategory(it) },
                onSearch = { query -> viewModel.searchTorrents(query) },
                onLoadTrending = { viewModel.loadTrending() },
                modifier = Modifier.width(320.dp).fillMaxHeight()
            )

            // Content Area
            ContentPanel(
                results = searchResults,
                isLoading = isLoading,
                currentMode = currentMode,
                onTorrentClick = { torrent -> viewModel.copyMagnetToClipboard(torrent) },
                modifier = Modifier.weight(1f).fillMaxHeight()
            )
        }
    }
}

@Composable
private fun SidebarPanel(
    selectedSites: Set<String>,
    selectedCategory: String,
    currentMode: String,
    onSitesChanged: (Set<String>) -> Unit,
    onCategoryChanged: (String) -> Unit,
    onSearch: (String) -> Unit,
    onLoadTrending: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.surfaceVariant,
        tonalElevation = 2.dp
    ) {
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Search Section
            item {
                SearchSection(
                    onSearch = onSearch,
                    onLoadTrending = onLoadTrending
                )
            }

            // Categories Section
            item {
                CategoriesSection(
                    selectedCategory = selectedCategory,
                    onCategoryChanged = onCategoryChanged
                )
            }

            // Sites Section
            item {
                SitesSection(
                    selectedSites = selectedSites,
                    onSitesChanged = onSitesChanged
                )
            }
        }
    }
}

@Composable
private fun ContentPanel(
    results: List<TorrentResult>,
    isLoading: Boolean,
    currentMode: String,
    onTorrentClick: (TorrentResult) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.background
    ) {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            // Content Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = when {
                        isLoading -> "🔍 Searching..."
                        currentMode == "trending" -> "📈 Trending Torrents"
                        results.isNotEmpty() -> "🚀 Search Results"
                        else -> "🚀 Ready to search"
                    },
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )

                if (results.isNotEmpty()) {
                    Text(
                        text = "${results.size} torrents found",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Results Content
            when {
                isLoading -> {
                    Box(modifier = Modifier.fillMaxSize()) {
                        CircularProgressIndicator(
                            modifier = Modifier.align(Alignment.Center)
                        )
                    }
                }
                results.isEmpty() -> {
                    EmptyStateContent()
                }
                else -> {
                    TorrentResultsList(
                        results = results,
                        onTorrentClick = onTorrentClick,
                        modifier = Modifier.fillMaxSize()
                    )
                }
            }
        }
    }
}

@Composable
private fun EmptyStateContent() {
    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.align(Alignment.Center),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "🔍",
                style = MaterialTheme.typography.displayLarge
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                "Enter a search term or browse trending torrents",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}