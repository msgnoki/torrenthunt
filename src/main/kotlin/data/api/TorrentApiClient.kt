package data.api

import data.models.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.client.request.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import kotlin.time.Duration.Companion.seconds

/**
 * TorrentHunt API Client
 * Handles all HTTP communication with the torrent search API
 */
class TorrentApiClient {

    companion object {
        private const val BASE_URL = "https://torrent-api-py-nx0x.onrender.com"
        private const val SEARCH_ENDPOINT = "/api/v1/search"
        private const val TRENDING_ENDPOINT = "/api/v1/trending"
        private const val REQUEST_TIMEOUT_SECONDS = 30L
        private const val MAX_CONCURRENT_REQUESTS = 7
    }

    private val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                coerceInputValues = true
                isLenient = true
            })
        }

        install(Logging) {
            logger = Logger.SIMPLE
            level = LogLevel.INFO
        }

        engine {
            requestTimeout = REQUEST_TIMEOUT_SECONDS.seconds.inWholeMilliseconds
        }
    }

    /**
     * Search torrents across multiple sites concurrently
     */
    suspend fun searchTorrents(
        query: String,
        sites: List<String>,
        category: String = "all"
    ): List<TorrentResult> = withContext(Dispatchers.IO) {

        if (query.isBlank() || sites.isEmpty()) {
            return@withContext emptyList()
        }

        // Launch concurrent requests for each site
        val deferredResults = sites.map { site ->
            async {
                try {
                    searchSingleSite(query, site, category)
                } catch (e: Exception) {
                    println("❌ Search error on $site: ${e.message}")
                    emptyList<TorrentResult>()
                }
            }
        }

        // Collect all results
        val allResults = deferredResults.awaitAll().flatten()

        // Add site metadata to results
        allResults.map { result ->
            val siteInfo = TorrentSite.AVAILABLE_SITES.find { it.key == result.sourceSite }
            result.copy(
                sourceIcon = siteInfo?.icon ?: "🔗",
                sourceName = siteInfo?.name ?: result.sourceSite,
                sourceColor = siteInfo?.color ?: "#666666"
            )
        }
    }

    /**
     * Get trending torrents from multiple sites
     */
    suspend fun getTrendingTorrents(
        sites: List<String>,
        category: String = "all",
        limit: Int = 50
    ): List<TorrentResult> = withContext(Dispatchers.IO) {

        if (sites.isEmpty()) {
            return@withContext emptyList()
        }

        val limitPerSite = (limit / sites.size).coerceAtLeast(10)

        // Launch concurrent requests for trending
        val deferredResults = sites.map { site ->
            async {
                try {
                    getTrendingSingleSite(site, limitPerSite)
                } catch (e: Exception) {
                    println("❌ Trending error on $site: ${e.message}")
                    emptyList<TorrentResult>()
                }
            }
        }

        // Collect and filter results
        val allResults = deferredResults.awaitAll().flatten()

        val filteredResults = if (category != "all") {
            allResults.filter { result ->
                matchesCategory(result.name, result.category ?: "", category)
            }
        } else {
            allResults
        }

        // Add site metadata and limit total results
        filteredResults.take(limit).map { result ->
            val siteInfo = TorrentSite.AVAILABLE_SITES.find { it.key == result.sourceSite }
            result.copy(
                sourceIcon = siteInfo?.icon ?: "🔗",
                sourceName = siteInfo?.name ?: result.sourceSite,
                sourceColor = siteInfo?.color ?: "#666666"
            )
        }
    }

    /**
     * Search a single site
     */
    private suspend fun searchSingleSite(
        query: String,
        site: String,
        category: String = "all"
    ): List<TorrentResult> {

        val response: ApiResponse = client.get("$BASE_URL$SEARCH_ENDPOINT") {
            parameter("query", query)
            parameter("site", site)
            parameter("limit", 25)
            if (category != "all") {
                parameter("category", category)
            }
        }.body()

        return response.data.map { result ->
            result.copy(sourceSite = site)
        }
    }

    /**
     * Get trending from a single site
     */
    private suspend fun getTrendingSingleSite(
        site: String,
        limit: Int = 20
    ): List<TorrentResult> {

        val response: ApiResponse = client.get("$BASE_URL$TRENDING_ENDPOINT") {
            parameter("site", site)
            parameter("limit", limit)
        }.body()

        return response.data.map { result ->
            result.copy(sourceSite = site)
        }
    }

    /**
     * Check if torrent matches category keywords
     */
    private fun matchesCategory(name: String, torrentCategory: String, targetCategory: String): Boolean {
        val category = TorrentCategory.AVAILABLE_CATEGORIES.find { it.key == targetCategory }
            ?: return true

        if (category.keywords.isEmpty()) return true

        val searchText = "${name.lowercase()} ${torrentCategory.lowercase()}"
        return category.keywords.any { keyword ->
            searchText.contains(keyword)
        }
    }

    /**
     * Close the HTTP client
     */
    fun close() {
        client.close()
    }
}