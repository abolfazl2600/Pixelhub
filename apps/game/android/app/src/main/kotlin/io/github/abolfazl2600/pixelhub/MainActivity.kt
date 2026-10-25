package io.github.abolfazl2600.pixelhub

import android.app.Activity
import android.content.ContentValues
import android.content.Intent
import android.media.AudioAttributes
import android.media.SoundPool
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.IOException

class MainActivity : FlutterActivity() {
    private var soundPool: SoundPool? = null
    private val soundIds = mutableMapOf<String, Int>()
    private val readyIds = mutableSetOf<Int>()
    private data class PendingGifSave(val bytes: ByteArray, val reply: MethodChannel.Result)
    private var pendingGifSave: PendingGifSave? = null

    companion object {
        private const val GIF_SAVE_REQUEST_CODE = 0x5109
        private const val MAX_GIF_BYTES = 16 * 1024 * 1024
    }

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

        // Save is deliberately separate from share: MediaStore makes the file
        // visible to Gallery/Photos on Android 10+, without storage permission.
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "pixelhub/timelapse_gif")
            .setMethodCallHandler { call, result ->
                if (call.method != "save") {
                    result.notImplemented()
                    return@setMethodCallHandler
                }
                val name = call.argument<String>("name")
                val bytes = call.argument<ByteArray>("bytes")
                if (name == null ||
                    !Regex("^[A-Za-z0-9][A-Za-z0-9._-]{0,119}\\.gif$").matches(name) ||
                    bytes == null ||
                    bytes.isEmpty() ||
                    bytes.size > MAX_GIF_BYTES
                ) {
                    result.error("gif_invalid", "Invalid GIF name or payload.", null)
                    return@setMethodCallHandler
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    Thread {
                        try {
                            saveGifToPictures(name, bytes)
                            runOnUiThread { result.success(true) }
                        } catch (error: Exception) {
                            runOnUiThread {
                                result.error("gif_save_failed", error.message, null)
                            }
                        }
                    }.start()
                } else {
                    // Before scoped storage, let the user select Downloads or
                    // Pictures through the system picker; no legacy permission.
                    if (pendingGifSave != null) {
                        result.error("gif_busy", "A GIF save is already in progress.", null)
                        return@setMethodCallHandler
                    }
                    pendingGifSave = PendingGifSave(bytes, result)
                    try {
                        val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                            addCategory(Intent.CATEGORY_OPENABLE)
                            type = "image/gif"
                            putExtra(Intent.EXTRA_TITLE, name)
                        }
                        startActivityForResult(intent, GIF_SAVE_REQUEST_CODE)
                    } catch (error: Exception) {
                        pendingGifSave = null
                        result.error("gif_save_failed", error.message, null)
                    }
                }
            }
    }

    private fun saveGifToPictures(name: String, bytes: ByteArray) {
        val values = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name)
            put(MediaStore.MediaColumns.MIME_TYPE, "image/gif")
            put(
                MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_PICTURES + "/PixelHub",
            )
            put(MediaStore.MediaColumns.IS_PENDING, 1)
        }
        val uri = contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            ?: throw IOException("Could not create image in Pictures.")
        try {
            val stream = contentResolver.openOutputStream(uri)
                ?: throw IOException("Could not open image output stream.")
            stream.use { output ->
                output.write(bytes)
                output.flush()
            }
            contentResolver.update(
                uri,
                ContentValues().apply { put(MediaStore.MediaColumns.IS_PENDING, 0) },
                null,
                null,
            )
        } catch (error: Exception) {
            contentResolver.delete(uri, null, null)
            throw error
        }
    }

    @Deprecated("Deprecated in Android; needed for Android 9 system file picker")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != GIF_SAVE_REQUEST_CODE) return
        val pending = pendingGifSave ?: return
        pendingGifSave = null
        val destination = data?.data
        if (resultCode != Activity.RESULT_OK || destination == null) {
            pending.reply.success(false)
            return
        }
        Thread {
            try {
                val stream = contentResolver.openOutputStream(destination, "w")
                    ?: throw IOException("Could not open selected destination.")
                stream.use { output ->
                    output.write(pending.bytes)
                    output.flush()
                }
                runOnUiThread { pending.reply.success(true) }
            } catch (error: Exception) {
                runOnUiThread {
                    pending.reply.error("gif_save_failed", error.message, null)
                }
            }
        }.start()
    }

    override fun cleanUpFlutterEngine(flutterEngine: FlutterEngine) {
        pendingGifSave?.reply?.success(false)
        pendingGifSave = null
        soundPool?.release()
        soundPool = null
        soundIds.clear()
        readyIds.clear()
        super.cleanUpFlutterEngine(flutterEngine)
    }
}
