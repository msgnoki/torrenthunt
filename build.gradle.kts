import org.jetbrains.compose.desktop.application.dsl.TargetFormat

plugins {
    kotlin("jvm") version "1.9.20"
    kotlin("plugin.serialization") version "1.9.20"
    id("org.jetbrains.compose") version "1.5.11"
}

group = "com.msgnoki"
version = "1.0.0"

repositories {
    mavenCentral()
    maven("https://maven.pkg.jetbrains.space/public/p/compose/dev")
    google()
}

dependencies {
    // Compose Desktop
    implementation(compose.desktop.currentOs)
    implementation(compose.material3)
    implementation(compose.materialIconsExtended)

    // Ktor HTTP Client
    implementation("io.ktor:ktor-client-core:2.3.5")
    implementation("io.ktor:ktor-client-cio:2.3.5")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.5")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")
    implementation("io.ktor:ktor-client-logging:2.3.5")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-swing:1.7.3")

    // JSON Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")

    // Replace Android-specific lifecycle with Kotlin state management
    // implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0") // Not compatible with Desktop
}

compose.desktop {
    application {
        mainClass = "MainKt"

        nativeDistributions {
            targetFormats(TargetFormat.Dmg, TargetFormat.Msi, TargetFormat.Deb, TargetFormat.Rpm)
            packageName = "TorrentHunt"
            packageVersion = "1.0.0"
            description = "Modern BitTorrent Search Client"
            copyright = "© 2024 msgnoki. All rights reserved."
            vendor = "msgnoki"

            linux {
                packageName = "torrenthunt-desktop"
                debMaintainer = "msgnoki@users.noreply.github.com"
                menuGroup = "Network"
                appCategory = "Network"
            }

            macOS {
                bundleID = "com.msgnoki.torrenthunt"
            }

            windows {
                menuGroup = "TorrentHunt"
                upgradeUuid = "61DAB35E-17CB-43B4-81F3-003F2E0DFB47"
            }
        }
    }
}

kotlin {
    jvmToolchain(17)
}