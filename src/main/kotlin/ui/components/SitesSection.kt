package ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import data.models.TorrentSite

/**
 * Sites Section Component
 * Checkbox selection for torrent sites
 */

@Composable
fun SitesSection(
    selectedSites: Set<String>,
    onSitesChanged: (Set<String>) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Section Title
        Text(
            text = "🌐 Torrent Sites",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )

        // Sites List
        TorrentSite.AVAILABLE_SITES.forEach { site ->
            SiteItem(
                site = site,
                selected = selectedSites.contains(site.key),
                onToggle = {
                    val newSites = selectedSites.toMutableSet()
                    if (newSites.contains(site.key)) {
                        newSites.remove(site.key)
                    } else {
                        newSites.add(site.key)
                    }
                    onSitesChanged(newSites)
                }
            )
        }

        // Selection Controls
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedButton(
                onClick = {
                    onSitesChanged(TorrentSite.AVAILABLE_SITES.map { it.key }.toSet())
                },
                modifier = Modifier.weight(1f)
            ) {
                Icon(
                    Icons.Default.CheckBox,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text("All", style = MaterialTheme.typography.bodySmall)
            }

            OutlinedButton(
                onClick = {
                    onSitesChanged(emptySet())
                },
                modifier = Modifier.weight(1f)
            ) {
                Icon(
                    Icons.Default.Clear,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text("None", style = MaterialTheme.typography.bodySmall)
            }
        }

        // Selection Counter
        Text(
            text = "${selectedSites.size} of ${TorrentSite.AVAILABLE_SITES.size} sites selected",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun SiteItem(
    site: TorrentSite,
    selected: Boolean,
    onToggle: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = selected,
            onCheckedChange = { onToggle() }
        )

        Spacer(modifier = Modifier.width(12.dp))

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "${site.icon} ${site.name}",
                style = MaterialTheme.typography.bodyMedium,
                color = if (selected) {
                    MaterialTheme.colorScheme.onSurface
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
                fontWeight = if (selected) FontWeight.Medium else FontWeight.Normal
            )

            if (site.description.isNotEmpty()) {
                Text(
                    text = site.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        // Site Status Indicator
        SiteStatusIndicator(
            enabled = site.enabled,
            selected = selected
        )
    }
}

@Composable
private fun SiteStatusIndicator(
    enabled: Boolean,
    selected: Boolean,
    modifier: Modifier = Modifier
) {
    val color = when {
        !enabled -> MaterialTheme.colorScheme.error
        selected -> MaterialTheme.colorScheme.primary
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    val icon = when {
        !enabled -> Icons.Default.Error
        selected -> Icons.Default.CheckCircle
        else -> Icons.Default.Circle
    }

    Icon(
        imageVector = icon,
        contentDescription = when {
            !enabled -> "Site unavailable"
            selected -> "Site selected"
            else -> "Site available"
        },
        tint = color,
        modifier = modifier.size(16.dp)
    )
}