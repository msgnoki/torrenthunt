package ui.viewmodels

import data.api.TorrentApiClient
import data.models.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection

/**
 * TorrentViewModel - Modern MVVM with StateFlow
 * Handles all business logic and state management
 */
class TorrentViewModel {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val apiClient = TorrentApiClient()

    // UI State
    private val _searchResults = MutableStateFlow<List<TorrentResult>>(emptyList())
    val searchResults: StateFlow<List<TorrentResult>> = _searchResults.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _currentMode = MutableStateFlow("search") // "search" or "trending"
    val currentMode: StateFlow<String> = _currentMode.asStateFlow()

    private val _selectedSites = MutableStateFlow(TorrentSite.AVAILABLE_SITES.map { it.key }.toSet())
    val selectedSites: StateFlow<Set<String>> = _selectedSites.asStateFlow()

    private val _selectedCategory = MutableStateFlow("all")
    val selectedCategory: StateFlow<String> = _selectedCategory.asStateFlow()

    private val _statusMessage = MutableStateFlow("Ready")
    val statusMessage: StateFlow<String> = _statusMessage.asStateFlow()

    private val _sortCriteria = MutableStateFlow(SortCriteria.SEEDERS)
    val sortCriteria: StateFlow<SortCriteria> = _sortCriteria.asStateFlow()

    private val _sortDescending = MutableStateFlow(true)
    val sortDescending: StateFlow<Boolean> = _sortDescending.asStateFlow()

    /**
     * Search torrents across selected sites
     */
    fun searchTorrents(query: String) {
        if (query.isBlank()) {
            _statusMessage.value = "Please enter a search term"
            return
        }

        if (_selectedSites.value.isEmpty()) {
            _statusMessage.value = "Please select at least one site"
            return
        }

        scope.launch {
            try {
                _isLoading.value = true
                _currentMode.value = "search"
                _statusMessage.value = "🔍 Searching torrents..."

                val results = apiClient.searchTorrents(
                    query = query,
                    sites = _selectedSites.value.toList(),
                    category = _selectedCategory.value
                )

                val sortedResults = sortResults(results)
                _searchResults.value = sortedResults
                _statusMessage.value = "✅ Found ${results.size} torrents"

            } catch (e: Exception) {
                _statusMessage.value = "❌ Search error: ${e.message}"
                _searchResults.value = emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Load trending torrents
     */
    fun loadTrending() {
        if (_selectedSites.value.isEmpty()) {
            _statusMessage.value = "Please select at least one site"
            return
        }

        scope.launch {
            try {
                _isLoading.value = true
                _currentMode.value = "trending"
                _statusMessage.value = "📈 Loading trending torrents..."

                val results = apiClient.getTrendingTorrents(
                    sites = _selectedSites.value.toList(),
                    category = _selectedCategory.value,
                    limit = 100
                )

                val sortedResults = sortResults(results)
                _searchResults.value = sortedResults
                _statusMessage.value = "✅ Loaded ${results.size} trending torrents"

            } catch (e: Exception) {
                _statusMessage.value = "❌ Trending error: ${e.message}"
                _searchResults.value = emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Update selected sites
     */
    fun updateSelectedSites(sites: Set<String>) {
        _selectedSites.value = sites
    }

    /**
     * Update selected category
     */
    fun updateSelectedCategory(category: String) {
        _selectedCategory.value = category
    }

    /**
     * Sort results by criteria
     */
    fun sortBy(criteria: SortCriteria, descending: Boolean = true) {
        _sortCriteria.value = criteria
        _sortDescending.value = descending
        _searchResults.value = sortResults(_searchResults.value)
    }

    /**
     * Copy magnet link to clipboard
     */
    fun copyMagnetToClipboard(torrent: TorrentResult) {
        try {
            val clipboard = Toolkit.getDefaultToolkit().systemClipboard
            val selection = StringSelection(torrent.magnet)
            clipboard.setContents(selection, null)

            val torrentName = torrent.name.take(40)
            _statusMessage.value = "📋 Magnet copied: $torrentName..."
        } catch (e: Exception) {
            _statusMessage.value = "❌ Failed to copy magnet link: ${e.message}"
        }
    }

    /**
     * Toggle site selection
     */
    fun toggleSite(siteKey: String) {
        val currentSites = _selectedSites.value.toMutableSet()
        if (currentSites.contains(siteKey)) {
            currentSites.remove(siteKey)
        } else {
            currentSites.add(siteKey)
        }
        _selectedSites.value = currentSites
    }

    /**
     * Select all sites
     */
    fun selectAllSites() {
        _selectedSites.value = TorrentSite.AVAILABLE_SITES.map { it.key }.toSet()
    }

    /**
     * Deselect all sites
     */
    fun deselectAllSites() {
        _selectedSites.value = emptySet()
    }

    /**
     * Internal sorting logic
     */
    private fun sortResults(results: List<TorrentResult>): List<TorrentResult> {
        val sorted = when (_sortCriteria.value) {
            SortCriteria.NAME -> results.sortedBy { it.name.lowercase() }
            SortCriteria.SIZE -> results.sortedBy { sizeToBytes(it.size) }
            SortCriteria.SEEDERS -> results.sortedBy { it.seedersCount }
            SortCriteria.LEECHERS -> results.sortedBy { it.leechersCount }
            SortCriteria.RATIO -> results.sortedBy { it.ratio }
            SortCriteria.DATE -> results.sortedBy { it.date ?: "" }
            SortCriteria.SOURCE -> results.sortedBy { it.sourceName }
        }

        return if (_sortDescending.value) sorted.reversed() else sorted
    }

    /**
     * Convert size string to bytes for sorting
     */
    private fun sizeToBytes(sizeStr: String): Long {
        if (sizeStr.isBlank() || sizeStr == "N/A") return 0L

        val size = sizeStr.uppercase()
        val multipliers = mapOf(
            "B" to 1L,
            "KB" to 1024L,
            "MB" to 1024L * 1024L,
            "GB" to 1024L * 1024L * 1024L,
            "TB" to 1024L * 1024L * 1024L * 1024L,
            "GIB" to 1024L * 1024L * 1024L,
            "MIB" to 1024L * 1024L,
            "KIB" to 1024L
        )

        for ((unit, multiplier) in multipliers) {
            if (unit in size) {
                return try {
                    val number = size.replace(unit, "").trim().toDoubleOrNull() ?: 0.0
                    (number * multiplier).toLong()
                } catch (e: Exception) {
                    0L
                }
            }
        }
        return 0L
    }

    /**
     * Cleanup resources
     */
    fun cleanup() {
        apiClient.close()
    }
}