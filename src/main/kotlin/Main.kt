/**
 * TorrentHunt Desktop - Native Kotlin Application
 * Modern BitTorrent search client with Compose Desktop
 *
 * @author msgnoki
 * @version 1.0.0
 */

import androidx.compose.desktop.ui.tooling.preview.Preview
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.window.WindowDraggableArea
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.*
import kotlinx.coroutines.DelicateCoroutinesApi
import ui.theme.TorrentHuntTheme
import ui.screens.MainScreen

@OptIn(DelicateCoroutinesApi::class)
fun main() = application {
    var isVisible by remember { mutableStateOf(true) }

    if (isVisible) {
        Window(
            onCloseRequest = {
                isVisible = false
                exitApplication()
            },
            title = "TorrentHunt Desktop",
            state = WindowState(
                placement = WindowPlacement.Floating,
                width = 1200.dp,
                height = 800.dp
            ),
            resizable = true
        ) {
            TorrentHuntTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen()
                }
            }
        }
    }
}

@Preview
@Composable
fun AppPreview() {
    TorrentHuntTheme {
        MainScreen()
    }
}