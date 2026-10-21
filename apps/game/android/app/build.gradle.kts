import groovy.json.JsonSlurper
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
val selectedProduct = System.getenv("PIXELHUB_BUILD_PRODUCT") ?: "pixelhub"
@Suppress("UNCHECKED_CAST")
val productRegistry = JsonSlurper().parse(rootProject.file("../../../products/android-products.json")) as List<Map<String, Any>>



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

    flavorDimensions += "product"
    productFlavors {
        productRegistry.forEach { product ->
            create(product["id"] as String) {
                dimension = "product"
                applicationId = product["applicationId"] as String
                versionName = product["versionName"] as String
                versionCode = (product["versionCode"] as Number).toInt()
                resValue("string", "app_name", product["name"] as String)
            }
        }
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
            // Signing is assigned only to the selected flavor below.
            signingConfig = null
        }
    }
    productFlavors.configureEach {
        if (name == selectedProduct && hasPlaySigning) {
            signingConfig = signingConfigs.getByName("playRelease")
        }
    }
}

// Never create an unsigned release or accidentally reuse another product's key.
gradle.taskGraph.whenReady {
    val releaseProducts = productRegistry.filter { product ->
        val variant = (product["id"] as String).replaceFirstChar { it.uppercase() } + "Release"
        allTasks.any { it.project == project && (it.name == "assemble$variant" || it.name == "bundle$variant" || it.name == "package$variant") }
    }
    if (releaseProducts.isNotEmpty()) {
        check(hasPlaySigning) { "Missing release signing environment; use preview-apk for testing." }
        check(releaseProducts.all { it["id"] == selectedProduct }) { "Build each release product separately with its own signing environment." }
    }
}

flutter {
    source = "../.."
}
