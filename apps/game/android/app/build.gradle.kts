plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

// Play signing is loaded only from private CI environment variables.
val signingKeys = listOf(
    "PIXELHUB_RELEASE_STORE_FILE",
    "PIXELHUB_RELEASE_STORE_PASSWORD",
    "PIXELHUB_RELEASE_KEY_ALIAS",
    "PIXELHUB_RELEASE_KEY_PASSWORD",
)
val hasPlaySigning = signingKeys.all { !System.getenv(it).isNullOrBlank() }


android {
    namespace = "io.github.abolfazl2600.pixelhub"
    compileSdk = 36
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        // Stable Play package identity; do not change after first upload.
        applicationId = "io.github.abolfazl2600.pixelhub"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = 36
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        if (hasPlaySigning) {
            create("playRelease") {
                storeFile = file(System.getenv("PIXELHUB_RELEASE_STORE_FILE"))
                storePassword = System.getenv("PIXELHUB_RELEASE_STORE_PASSWORD")
                keyAlias = System.getenv("PIXELHUB_RELEASE_KEY_ALIAS")
                keyPassword = System.getenv("PIXELHUB_RELEASE_KEY_PASSWORD")
            }
        }
    }
    buildTypes {
        release {
            // Do not silently fall back to the Android debug certificate.
            if (hasPlaySigning) {
                signingConfig = signingConfigs.getByName("playRelease")
            }
        }
    }
}

flutter {
    source = "../.."
}
