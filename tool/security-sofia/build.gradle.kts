plugins {
    id("com.android.application")
    id("dev.flutter.flutter-gradle-plugin")
}

val releaseStore = System.getenv("VAMOS_RELEASE_KEYSTORE_PATH")
val releaseStorePassword = System.getenv("VAMOS_RELEASE_STORE_PASSWORD")
val releaseKeyPassword = System.getenv("VAMOS_RELEASE_KEY_PASSWORD")
val releaseAlias = System.getenv("VAMOS_RELEASE_KEY_ALIAS")
val signingReady = listOf(releaseStore, releaseStorePassword, releaseKeyPassword, releaseAlias).all { !it.isNullOrBlank() }
val releaseRequested = gradle.startParameter.taskNames.any { it.contains("release", ignoreCase = true) }
if (releaseRequested && !signingReady) {
    throw GradleException("Falta configurar la firma de producción de INGENIX. Consulta tool/security-sofia/README.md. No se permite sustituirla por una firma debug.")
}

android {
    namespace = "com.vamoscarpool.app"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    defaultConfig {
        applicationId = "com.vamoscarpool.app"
        minSdk = 31
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }
    signingConfigs {
        if (signingReady) {
            create("production") {
                storeFile = file(releaseStore!!)
                storePassword = releaseStorePassword
                keyAlias = releaseAlias
                keyPassword = releaseKeyPassword
            }
        }
    }
    buildTypes {
        release {
            isDebuggable = false
            if (signingReady) signingConfig = signingConfigs.getByName("production")
        }
    }
}
kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter { source = "../.." }
