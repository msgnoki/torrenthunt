package ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp

/**
 * Search Section Component
 * Contains search input and trending button
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchSection(
    onSearch: (String) -> Unit,
    onLoadTrending: () -> Unit,
    modifier: Modifier = Modifier
) {
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Section Title
        Text(
            text = "🔍 Search",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )

        // Search Input
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Enter search term...") },
            leadingIcon = {
                Icon(Icons.Default.Search, contentDescription = "Search icon")
            },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { searchQuery = "" }) {
                        Icon(Icons.Default.Clear, contentDescription = "Clear search")
                    }
                }
            },
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            keyboardActions = KeyboardActions(
                onSearch = {
                    if (searchQuery.isNotBlank()) {
                        onSearch(searchQuery)
                    }
                }
            ),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        // Action Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Search Button
            Button(
                onClick = {
                    if (searchQuery.isNotBlank()) {
                        onSearch(searchQuery)
                    }
                },
                modifier = Modifier.weight(1f),
                enabled = searchQuery.isNotBlank()
            ) {
                Icon(
                    Icons.Default.Search,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Search")
            }
        }

        // Trending Button
        OutlinedButton(
            onClick = onLoadTrending,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(
                Icons.Default.TrendingUp,
                contentDescription = null,
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("📈 View Trending")
        }

        // Quick Search Suggestions
        QuickSearchChips(
            onQuickSearch = { query ->
                searchQuery = query
                onSearch(query)
            }
        )
    }
}

@Composable
private fun QuickSearchChips(
    onQuickSearch: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val quickSearches = listOf(
        "movies 2024",
        "tv series",
        "music flac",
        "games pc",
        "software",
        "books pdf"
    )

    Column(modifier = modifier) {
        Text(
            text = "Quick searches:",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Wrap chips in rows
        quickSearches.chunked(2).forEach { rowChips ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                rowChips.forEach { search ->
                    SuggestionChip(
                        onClick = { onQuickSearch(search) },
                        label = {
                            Text(
                                search,
                                style = MaterialTheme.typography.bodySmall
                            )
                        },
                        modifier = Modifier.weight(1f)
                    )
                }
                // Fill remaining space if odd number
                if (rowChips.size == 1) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
        }
    }
}