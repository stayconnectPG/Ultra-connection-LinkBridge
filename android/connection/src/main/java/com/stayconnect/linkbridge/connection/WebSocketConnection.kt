package com.stayconnect.linkbridge.connection

import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import java.util.concurrent.TimeUnit

data class WsMessage(
    val type: String,
    val payload: Map<String, Any?> = emptyMap(),
) {
    companion object {
        fun fromJson(json: String): WsMessage {
            // Minimal parser — Phase 1; will use Moshi/Jackson in Phase 2
            return WsMessage(type = "message", payload = mapOf("raw" to json))
        }
    }

    fun toJson(): String {
        return """{"type":"$type","payload":${payload}}"""
    }
}

enum class ConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    RECONNECTING,
    ERROR,
}

interface ConnectionListener {
    fun onConnected()
    fun onDisconnected()
    fun onError(error: Throwable)
    fun onMessage(message: WsMessage)
}

class WebSocketConnection(
    private val serverUrl: String,
    private val token: String? = null,
) {

    private val _state = MutableStateFlow(ConnectionState.DISCONNECTED)
    val state: StateFlow<ConnectionState> = _state.asStateFlow()

    private val _messages = Channel<WsMessage>(Channel.BUFFERED)
    val messages = _messages.receiveAsFlow()

    private var webSocket: WebSocket? = null
    private var listener: ConnectionListener? = null
    private var reconnectJob: kotlinx.coroutines.Job? = null

    private val client = OkHttpClient.Builder()
        .pingInterval(20, TimeUnit.SECONDS)
        .build()

    fun connect(stateListener: ConnectionListener) {
        this.listener = stateListener
        _state.value = ConnectionState.CONNECTING
        val request = Request.Builder()
            .url(serverUrl)
            .header("Authorization", "Bearer ${token ?: ""}")
            .build()
        webSocket = client.newWebSocket(request, socketListener)
    }

    fun disconnect() {
        reconnectJob?.cancel()
        reconnectJob = null
        webSocket?.close(1000, "Normal closure")
        webSocket = null
        _state.value = ConnectionState.DISCONNECTED
    }

    fun send(message: WsMessage) {
        val ws = webSocket
        if (ws == null || _state.value != ConnectionState.CONNECTED) {
            listener?.onError(IllegalStateException("Not connected"))
            return
        }
        ws.send(message.toJson())
    }

    private val socketListener = object : WebSocketListener() {
        override fun onOpen(ws: WebSocket, response: Response) {
            _state.value = ConnectionState.CONNECTED
            listener?.onConnected()
        }

        override fun onMessage(ws: WebSocket, text: String) {
            val msg = WsMessage.fromJson(text)
            listener?.onMessage(msg)
        }

        override fun onMessage(ws: WebSocket, bytes: ByteString) {
            onMessage(ws, bytes.utf8())
        }

        override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
            _state.value = ConnectionState.ERROR
            listener?.onError(t)
            scheduleReconnect()
        }

        override fun onClosing(ws: WebSocket, code: Int, reason: String) {
            _state.value = ConnectionState.DISCONNECTED
            listener?.onDisconnected()
        }
    }

    private fun scheduleReconnect() {
        // Phase 2: implement exponential backoff
    }
}
