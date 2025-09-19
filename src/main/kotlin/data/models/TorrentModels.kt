package data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Core data models for TorrentHunt
 * Clean, immutable data classes with serialization support
 */

@Serializable
data class TorrentResult(
    val name: String,
    val size: String,
    val seeders: Int = 0,
    val leechers: Int = 0,
    val magnet: String,
    @SerialName("url") val torrentUrl: String? = null,
    val category: String? = null,
    val uploader: String? = null,
    val date: String? = null,
    val hash: String? = null,

    // UI metadata (not from API)
    val sourceSite: String = "",
    val sourceIcon: String = "🔗",
    val sourceName: String = "",
    val sourceColor: String = "#666666"
) {
    val seedersCount: Int get() = seeders.coerceAtLeast(0)
    val leechersCount: Int get() = leechers.coerceAtLeast(0)
    val ratio: Float get() = if (leechersCount > 0) seedersCount.toFloat() / leechersCount else Float.MAX_VALUE

    val qualityScore: TorrentQuality get() = when {
        seedersCount >= 100 -> TorrentQuality.EXCELLENT
        seedersCount >= 50 -> TorrentQuality.GOOD
        seedersCount >= 10 -> TorrentQuality.AVERAGE
        else -> TorrentQuality.POOR
    }
}

@Serializable
data class ApiResponse(
    val data: List<TorrentResult> = emptyList(),
    val time: Double? = null,
    val total: Int? = null
)

data class TorrentSite(
    val key: String,
    val name: String,
    val icon: String,
    val color: String = "#666666",
    val enabled: Boolean = true,
    val description: String = ""
) {
    companion object {
        val AVAILABLE_SITES = listOf(
            TorrentSite("piratebay", "The Pirate Bay", "🏴‍☠️", "#e01b24", true, "Most popular torrent site"),
            TorrentSite("1337x", "1337x", "🔥", "#f57c00", true, "High quality releases"),
            TorrentSite("torrentgalaxy", "TorrentGalaxy", "🌌", "#9141ac", true, "Modern torrent community"),
            TorrentSite("rarbg", "RARBG", "💎", "#3584e4", true, "Quality over quantity"),
            TorrentSite("nyaa", "Nyaa", "🎌", "#e01b24", true, "Anime & Asian content"),
            TorrentSite("yts", "YTS", "🎬", "#26a269", true, "Movie focused site"),
            TorrentSite("eztv", "EZTV", "📺", "#613583", true, "TV shows specialist")
        )
    }
}

data class TorrentCategory(
    val key: String,
    val name: String,
    val icon: String,
    val description: String,
    val keywords: List<String> = emptyList()
) {
    companion object {
        val AVAILABLE_CATEGORIES = listOf(
            TorrentCategory("all", "All Content", "⭐", "All torrents", emptyList()),
            TorrentCategory("movies", "Movies", "🎬", "Films & Cinema",
                listOf("movie", "film", "cinema", "dvd", "bluray", "1080p", "720p", "4k")),
            TorrentCategory("tv", "TV Shows", "📺", "Series & Episodes",
                listOf("s01", "s02", "s03", "season", "episode", "tv", "series", "hdtv")),
            TorrentCategory("music", "Music", "🎵", "Audio & Albums",
                listOf("music", "audio", "mp3", "flac", "album", "song", "artist")),
            TorrentCategory("books", "Books", "📚", "eBooks & Magazines",
                listOf("book", "ebook", "pdf", "epub", "mobi", "magazine", "novel")),
            TorrentCategory("games", "Games", "🎮", "PC & Console Games",
                listOf("game", "pc", "xbox", "playstation", "nintendo", "steam")),
            TorrentCategory("software", "Software", "💻", "Applications & Tools",
                listOf("software", "app", "program", "windows", "mac", "linux")),
            TorrentCategory("anime", "Anime", "🎌", "Japanese Animation",
                listOf("anime", "manga", "subbed", "dubbed", "japanese"))
        )
    }
}

enum class TorrentQuality(val displayName: String, val color: Long) {
    EXCELLENT("Excellent", 0xFF26a269),
    GOOD("Good", 0xFF2ec27e),
    AVERAGE("Average", 0xFFf57c00),
    POOR("Poor", 0xFFe01b24)
}

enum class SortCriteria(val displayName: String) {
    NAME("Name"),
    SIZE("Size"),
    SEEDERS("Seeders"),
    LEECHERS("Leechers"),
    RATIO("Ratio"),
    DATE("Date"),
    SOURCE("Source")
}

data class SearchFilters(
    val selectedSites: Set<String> = TorrentSite.AVAILABLE_SITES.map { it.key }.toSet(),
    val selectedCategory: String = "all",
    val sortBy: SortCriteria = SortCriteria.SEEDERS,
    val sortDescending: Boolean = true,
    val minSeeders: Int = 0,
    val hideZeroSeeders: Boolean = false
)