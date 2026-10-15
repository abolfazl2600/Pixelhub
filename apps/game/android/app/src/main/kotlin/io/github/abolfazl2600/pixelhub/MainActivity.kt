package io.github.abolfazl2600.pixelhub

import android.media.AudioAttributes
import android.media.SoundPool
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File

class MainActivity : FlutterActivity() {
    private var soundPool: SoundPool? = null
    private val soundIds = mutableMapOf<String, Int>()
    private val readyIds = mutableSetOf<Int>()

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        val attributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_GAME)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()
        val pool = SoundPool.Builder()
            .setMaxStreams(2)
            .setAudioAttributes(attributes)
            .build()
        soundPool = pool
        pool.setOnLoadCompleteListener { _, sampleId, status ->
            if (status == 0) readyIds.add(sampleId)
        }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "pixelhub/sounds")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "load" -> {
                        val name = call.argument<String>("name")
                        val bytes = call.argument<ByteArray>("bytes")
                        if (name == null || name !in setOf("coin_purchase", "coins_earned", "painting_completed") ||
                            bytes == null || bytes.size > 192000
                        ) {
                            result.error("invalid_sound", "Invalid sound asset.", null)
                            return@setMethodCallHandler
                        }
                        try {
                            val file = File(cacheDir, "pixelhub_" + name + ".wav")
                            file.writeBytes(bytes)
                            val sampleId = pool.load(file.absolutePath, 1)
                            soundIds[name] = sampleId
                            result.success(null)
                        } catch (error: Exception) {
                            result.error("sound_load", error.message, null)
                        }
                    }
                    "play" -> {
                        val name = call.argument<String>("name")
                        val sampleId = if (name != null) soundIds[name] else null
                        if (sampleId != null && readyIds.contains(sampleId)) {
                            pool.play(sampleId, 0.45f, 0.45f, 1, 0, 1.0f)
                        }
                        result.success(null)
                    }
                    else -> result.notImplemented()
                }
            }
    }

    override fun cleanUpFlutterEngine(flutterEngine: FlutterEngine) {
        soundPool?.release()
        soundPool = null
        soundIds.clear()
        readyIds.clear()
        super.cleanUpFlutterEngine(flutterEngine)
    }
}
