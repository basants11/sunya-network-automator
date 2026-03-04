package com.sunya.networking

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

private const val TAG = "NetworkChangeReceiver"

class NetworkChangeReceiver : BroadcastReceiver() {

    private var currentNetworkType: String? = null

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            ConnectivityManager.CONNECTIVITY_ACTION -> {
                handleConnectivityChange(context)
            }
            "android.net.wifi.WIFI_STATE_CHANGED" -> {
                handleWifiStateChange(context)
            }
            "android.net.wifi.STATE_CHANGE" -> {
                handleWifiStateChange(context)
            }
            else -> {
                Log.d(TAG, "Unknown broadcast action: ${intent.action}")
            }
        }
    }

    private fun handleConnectivityChange(context: Context) {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val activeNetwork = connectivityManager.activeNetwork ?: return
        val networkCapabilities = connectivityManager.getNetworkCapabilities(activeNetwork) ?: return

        val networkType = when {
            networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "Wi-Fi"
            networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "Cellular"
            networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "Ethernet"
            else -> "Unknown"
        }

        // Trigger diagnostics only if network type changed or first connection
        if (currentNetworkType != networkType) {
            Log.d(TAG, "Network type changed from $currentNetworkType to $networkType")
            currentNetworkType = networkType
            triggerDiagnostics(context)
        }
    }

    private fun handleWifiStateChange(context: Context) {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val activeNetwork = connectivityManager.activeNetwork ?: return
        val networkCapabilities = connectivityManager.getNetworkCapabilities(activeNetwork) ?: return

        if (networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
            Log.d(TAG, "Wi-Fi connection detected")
            triggerDiagnostics(context)
        }
    }

    private fun triggerDiagnostics(context: Context) {
        Log.d(TAG, "Triggering diagnostics...")

        val serviceIntent = Intent(context, SunyaBackgroundService::class.java)
        SunyaBackgroundService.enqueueWork(context)

        // Also start foreground service for better reliability on newer Android versions
        val foregroundIntent = Intent(context, SunyaForegroundService::class.java)
        context.startForegroundService(foregroundIntent)
    }

    // Register for network callbacks for more reliable detection on Android 7.0+
    fun registerNetworkCallbacks(context: Context) {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val networkRequest = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            .build()

        connectivityManager.registerNetworkCallback(networkRequest, object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                Log.d(TAG, "Network available")
                triggerDiagnostics(context)
            }

            override fun onLost(network: Network) {
                Log.d(TAG, "Network lost")
                currentNetworkType = null
            }

            override fun onCapabilitiesChanged(
                network: Network,
                networkCapabilities: NetworkCapabilities
            ) {
                Log.d(TAG, "Network capabilities changed")
                triggerDiagnostics(context)
            }
        })
    }
}