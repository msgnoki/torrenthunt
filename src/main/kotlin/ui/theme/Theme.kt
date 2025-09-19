package ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/**
 * TorrentHunt Theme System
 * Dark/Light theme support inspired by our Python version
 */

// Dark Theme Colors
private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF3584e4),
    onPrimary = Color(0xFFffffff),
    primaryContainer = Color(0xFF2563c7),
    onPrimaryContainer = Color(0xFFffffff),

    secondary = Color(0xFF26a269),
    onSecondary = Color(0xFFffffff),
    secondaryContainer = Color(0xFF2ecc71),
    onSecondaryContainer = Color(0xFFffffff),

    tertiary = Color(0xFF9141ac),
    onTertiary = Color(0xFFffffff),

    error = Color(0xFFe01b24),
    onError = Color(0xFFffffff),
    errorContainer = Color(0xFFda3450),
    onErrorContainer = Color(0xFFffffff),

    background = Color(0xFF2b2b2b),
    onBackground = Color(0xFFffffff),
    surface = Color(0xFF363636),
    onSurface = Color(0xFFffffff),
    surfaceVariant = Color(0xFF404040),
    onSurfaceVariant = Color(0xFFffffff),

    outline = Color(0xFF555555),
    outlineVariant = Color(0xFF777777)
)

// Light Theme Colors
private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF3584e4),
    onPrimary = Color(0xFFffffff),
    primaryContainer = Color(0xFFe8f4f8),
    onPrimaryContainer = Color(0xFF2e3436),

    secondary = Color(0xFF26a269),
    onSecondary = Color(0xFFffffff),
    secondaryContainer = Color(0xFFe8f5e8),
    onSecondaryContainer = Color(0xFF2e3436),

    tertiary = Color(0xFF9141ac),
    onTertiary = Color(0xFFffffff),

    error = Color(0xFFe01b24),
    onError = Color(0xFFffffff),
    errorContainer = Color(0xFFfef2f2),
    onErrorContainer = Color(0xFF2e3436),

    background = Color(0xFFfafafa),
    onBackground = Color(0xFF2e3436),
    surface = Color(0xFFffffff),
    onSurface = Color(0xFF2e3436),
    surfaceVariant = Color(0xFFf0f0f0),
    onSurfaceVariant = Color(0xFF2e3436),

    outline = Color(0xFFd5d5d5),
    outlineVariant = Color(0xFFe0e0e0)
)

// Torrent Quality Colors
object TorrentColors {
    val excellent = Color(0xFF26a269)
    val good = Color(0xFF2ec27e)
    val average = Color(0xFFf57c00)
    val poor = Color(0xFFe01b24)

    val piratebay = Color(0xFFe01b24)
    val x1337 = Color(0xFFf57c00)
    val torrentgalaxy = Color(0xFF9141ac)
    val rarbg = Color(0xFF3584e4)
    val nyaa = Color(0xFFe01b24)
    val yts = Color(0xFF26a269)
    val eztv = Color(0xFF613583)
}

@Composable
fun TorrentHuntTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}