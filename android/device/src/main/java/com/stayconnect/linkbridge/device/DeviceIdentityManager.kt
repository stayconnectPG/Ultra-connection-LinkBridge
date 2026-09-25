package com.stayconnect.linkbridge.device

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.SecureRandom
import java.util.UUID

data class DeviceInfo(
    val deviceId: String,
    val platform: String = "android",
    val type: String = "android",
    val publicKey: String = "",
)

class DeviceIdentityManager(private val context: Context) {

    private val prefs = context.getSharedPreferences("linkbridge_device", Context.MODE_PRIVATE)
    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    fun getOrCreateIdentity(): DeviceInfo {
        var deviceId = prefs.getString("device_id", null)
        if (deviceId == null) {
            deviceId = "android-${UUID.randomUUID().toString().take(8)}"
            prefs.edit().putString("device_id", deviceId).apply()
        }
        return DeviceInfo(
            deviceId = deviceId,
            publicKey = getOrGeneratePublicKey(),
        )
    }

    fun getAccessToken(): String? = prefs.getString("access_token", null)

    fun saveAccessToken(token: String) {
        prefs.edit().putString("access_token", token).apply()
    }

    fun getSessionToken(): String? = prefs.getString("session_token", null)

    fun saveSessionToken(token: String) {
        prefs.edit().putString("session_token", token).apply()
    }

    private fun getOrGeneratePublicKey(): String {
        val alias = "linkbridge_key"
        if (!keyStore.containsAlias(alias)) {
            val keyPairGenerator = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_RSA, "AndroidKeyStore"
            )
            val spec = KeyGenParameterSpec.Builder(
                alias,
                KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY,
            )
                .setDigests(KeyProperties.DIGEST_SHA256, KeyProperties.DIGEST_SHA512)
                .setSignaturePaddings(KeyProperties.SIGNATURE_PADDING_RSA_PKCS1)
                .build()
            keyPairGenerator.initialize(spec)
            keyPairGenerator.generateKeyPair()
        }
        val publicKey = keyStore.getEntry(alias, null) as? KeyStore.PrivateKeyEntry
        return publicKey?.certificate?.publicKey?.toString() ?: ""
    }
}
