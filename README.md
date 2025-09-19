# 🏴‍☠️ TorrentHunt Desktop

**Modern BitTorrent Search Client Built with Kotlin + Compose Desktop**

![TorrentHunt](https://img.shields.io/badge/Kotlin-1.9.20-7F52FF?logo=kotlin)
![Compose](https://img.shields.io/badge/Compose-1.5.11-4285F4?logo=jetpackcompose)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

> **A native desktop application for searching torrents across multiple sites with a modern, responsive UI**

---

## ✨ Features

🔍 **Multi-Site Search** - Search across 7+ popular torrent sites simultaneously
📈 **Trending Torrents** - Browse popular content by categories
🎨 **Modern UI** - Material 3 design with dark/light theme support
📋 **One-Click Copy** - Copy magnet links directly to clipboard
⚡ **Native Performance** - Built with Kotlin coroutines for smooth experience
🐧 **Linux-First** - Optimized for Linux desktop environments

---

## 🚀 Quick Start

### Prerequisites
- **Java 17+** (OpenJDK recommended)
- **Linux/Windows/macOS**

### Installation

#### 📦 Ubuntu/Debian Package
```bash
# Download and install .deb package
sudo dpkg -i torrenthunt-desktop_1.0.0-1_amd64.deb

# Launch from applications menu or terminal
torrenthunt-desktop
```

#### 🏗️ Build from Source
```bash
# Clone repository
git clone https://github.com/msgnoki/torrenthunt.git
cd torrenthunt

# Install Gradle (Ubuntu/Debian)
sudo apt update && sudo apt install -y openjdk-17-jdk gradle

# Build and run
./gradlew run

# Create native packages
./gradlew packageDistributionForCurrentOS
```

---

## 🎯 Supported Sites

| Site | Icon | Specialty |
|------|------|-----------|
| **The Pirate Bay** | 🏴‍☠️ | Most popular torrent site |
| **1337x** | 🔥 | High quality releases |
| **TorrentGalaxy** | 🌌 | Modern community |
| **RARBG** | 💎 | Quality over quantity |
| **Nyaa** | 🎌 | Anime & Asian content |
| **YTS** | 🎬 | Movie focused |
| **EZTV** | 📺 | TV shows specialist |

---

## 🛠️ Technology Stack

### **Frontend**
- **Compose Desktop** - Declarative UI framework
- **Material 3** - Google's latest design system
- **Kotlin Coroutines** - Structured concurrency

### **Backend**
- **Ktor Client** - Async HTTP networking
- **Kotlinx Serialization** - JSON parsing
- **StateFlow** - Reactive state management

### **Build & Distribution**
- **Gradle** - Build automation
- **JPackage** - Native OS packages
- **Compose Multiplatform** - Cross-platform support

---

## 📱 User Interface

### Search Interface
- **Smart search** across multiple torrent sites
- **Category filtering** (Movies, TV, Music, Books, Games, Software, Anime)
- **Site selection** with checkboxes
- **Real-time results** with quality indicators

### Results Display
- **Card-based layout** with torrent details
- **Quality indicators** (Excellent/Good/Average/Poor)
- **Sort by** name, size, seeders, leechers, date
- **One-click magnet copy** to clipboard

### Trending Section
- **Popular torrents** by category
- **Fresh content** from all supported sites
- **Browse mode** for discovery

---

## ⚡ Performance

| Metric | TorrentHunt Kotlin | Typical Python App |
|--------|-------------------|-------------------|
| **Startup Time** | ~1.5s | ~3s |
| **Memory Usage** | ~120MB | ~150MB |
| **UI Responsiveness** | Native | Variable |
| **Network Concurrency** | Coroutines | Threading |
| **Package Size** | 79MB | 37MB+ |

---

## 🏗️ Development

### Project Structure
```
TorrentHunt/
├── build.gradle.kts              # Build configuration
├── src/main/kotlin/
│   ├── Main.kt                   # Application entry point
│   ├── data/
│   │   ├── models/               # Data classes & DTOs
│   │   └── api/                  # HTTP client & API logic
│   └── ui/
│       ├── theme/                # Material 3 theming
│       ├── screens/              # Main application screen
│       ├── components/           # Reusable UI components
│       └── viewmodels/           # MVVM business logic
└── gradle/                       # Gradle wrapper
```

### Building

```bash
# Development build
./gradlew build

# Run application
./gradlew run

# Create distribution packages
./gradlew packageDistributionForCurrentOS

# Clean build
./gradlew clean build
```

### Packaging

```bash
# Ubuntu/Debian (.deb)
./gradlew packageDeb

# Fedora/RHEL (.rpm)
./gradlew packageRpm

# Windows (.msi)
./gradlew packageMsi

# macOS (.dmg)
./gradlew packageDmg
```

---

## 🔧 Configuration

### API Configuration
The application uses the TorrentHunt API:
- **Base URL:** `https://torrent-api-py-nx0x.onrender.com`
- **Endpoints:** `/api/v1/search`, `/api/v1/trending`
- **Rate Limiting:** Built-in request throttling

### Customization
- **Theme:** Automatic dark/light mode detection
- **Sites:** Enable/disable individual torrent sites
- **Categories:** Filter content by type
- **Sorting:** Customize result ordering

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** Pull Request

### Development Guidelines
- Follow Kotlin coding conventions
- Use Compose best practices
- Write descriptive commit messages
- Test on multiple platforms

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **TorrentHunt API** - Reliable torrent search backend
- **JetBrains Compose** - Modern declarative UI framework
- **Material Design** - Consistent design language
- **Kotlin Community** - Amazing language and ecosystem

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/msgnoki/torrenthunt/issues)
- **Discussions:** [GitHub Discussions](https://github.com/msgnoki/torrenthunt/discussions)
- **Email:** msgnoki@users.noreply.github.com

---

<div align="center">

**Made with ❤️ and ☕ by [msgnoki](https://github.com/msgnoki)**

*Star ⭐ this repo if you find it useful!*

</div>