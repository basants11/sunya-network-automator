package com.sunya.networking

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.telephony.TelephonyManager
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.withContext
import java.net.InetAddress
import java.net.Socket
import java.net.URL
import java.util.concurrent.TimeUnit

private const val TAG = "SunyaCore"

class SunyaCore(private val context: Context) {

    // Network Fingerprint Data Class
    data class NetworkFingerprint(
        val interfaceType: String,
        val localIp: String,
        val gateway: String,
        val dns: List<String>,
        val ssid: String? = null,
        val mobileNetwork: String? = null,
        val timestamp: Long = System.currentTimeMillis()
    )

    // Diagnostic Results Data Class
    data class DiagnosticResult(
        val timestamp: Long,
        val fingerprint: NetworkFingerprint,
        val pingResults: PingResults,
        val tracerouteResults: TracerouteResults,
        val speedtestResults: SpeedtestResults,
        val diagnosis: String,
        val recommendations: List<String>
    )

    // Ping Results
    data class PingResults(
        val gatewayLoss: Double,
        val gatewayLatency: Double,
        val dnsLoss: Double,
        val dnsLatency: Double,
        val googleLoss: Double,
        val googleLatency: Double,
        val jitter: Double
    )

    // Traceroute Results
    data class TracerouteResults(
        val hops: List<Hop>,
        val firstLossHop: Int,
        val latencySpikes: List<Int>
    )

    data class Hop(
        val number: Int,
        val ip: String,
        val latency: Double
    )

    // Speedtest Results
    data class SpeedtestResults(
        val downloadSpeed: Double,
        val uploadSpeed: Double,
        val latency: Double,
        val consistency: Double
    )

    /**
     * Generate unique network fingerprint
     */
    fun generateNetworkFingerprint(): NetworkFingerprint? {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val activeNetwork = connectivityManager.activeNetwork ?: return null
        val networkCapabilities = connectivityManager.getNetworkCapabilities(activeNetwork) ?: return null

        return when {
            networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> {
                getWifiFingerprint()
            }
            networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> {
                getCellularFingerprint()
            }
            networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> {
                getEthernetFingerprint()
            }
            else -> {
                null
            }
        }
    }

    private fun getWifiFingerprint(): NetworkFingerprint {
        val wifiManager = context.getSystemService(Context.WIFI_SERVICE) as WifiManager
        val dhcpInfo = wifiManager.dhcpInfo

        return NetworkFingerprint(
            interfaceType = "Wi-Fi",
            localIp = intToIp(dhcpInfo.ipAddress),
            gateway = intToIp(dhcpInfo.gateway),
            dns = listOf(intToIp(dhcpInfo.dns1), intToIp(dhcpInfo.dns2)),
            ssid = wifiManager.connectionInfo.ssid.replace("\"", ""),
            mobileNetwork = null
        )
    }

    private fun getCellularFingerprint(): NetworkFingerprint {
        val telephonyManager = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager

        return NetworkFingerprint(
            interfaceType = "Cellular",
            localIp = getLocalIpAddress(),
            gateway = getDefaultGateway(),
            dns = getDnsServers(),
            ssid = null,
            mobileNetwork = telephonyManager.networkOperatorName
        )
    }

    private fun getEthernetFingerprint(): NetworkFingerprint {
        return NetworkFingerprint(
            interfaceType = "Ethernet",
            localIp = getLocalIpAddress(),
            gateway = getDefaultGateway(),
            dns = getDnsServers(),
            ssid = null,
            mobileNetwork = null
        )
    }

    private fun intToIp(address: Int): String {
        return ((address and 0xFF).toString() + "." +
                (address shr 8 and 0xFF) + "." +
                (address shr 16 and 0xFF) + "." +
                (address shr 24 and 0xFF))
    }

    private fun getLocalIpAddress(): String {
        return try {
            val interfaces = java.net.NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val intf = interfaces.nextElement()
                val addresses = intf.inetAddresses
                while (addresses.hasMoreElements()) {
                    val addr = addresses.nextElement()
                    if (!addr.isLoopbackAddress && addr.hostAddress.contains(".")) {
                        return addr.hostAddress
                    }
                }
            }
            "Unknown"
        } catch (e: Exception) {
            Log.e(TAG, "Error getting local IP: ${e.message}")
            "Unknown"
        }
    }

    private fun getDefaultGateway(): String {
        return try {
            val runtime = Runtime.getRuntime()
            val process = runtime.exec("/system/bin/ip route show")
            val reader = process.inputStream.bufferedReader()
            var gateway = "Unknown"

            reader.forEachLine { line ->
                if (line.contains("default")) {
                    val parts = line.split(" ")
                    gateway = parts[2]
                }
            }

            process.waitFor(1000, TimeUnit.MILLISECONDS)
            gateway
        } catch (e: Exception) {
            Log.e(TAG, "Error getting gateway: ${e.message}")
            "Unknown"
        }
    }

    private fun getDnsServers(): List<String> {
        return try {
            val runtime = Runtime.getRuntime()
            val process = runtime.exec("/system/bin/getprop")
            val reader = process.inputStream.bufferedReader()
            val dnsServers = mutableListOf<String>()

            reader.forEachLine { line ->
                if (line.contains("net.dns") && line.contains(":")) {
                    val value = line.split(":")[1].trim()
                    if (value.contains(".")) {
                        dnsServers.add(value)
                    }
                }
            }

            process.waitFor(1000, TimeUnit.MILLISECONDS)

            if (dnsServers.isEmpty()) {
                listOf("8.8.8.8", "1.1.1.1")
            } else {
                dnsServers.distinct()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error getting DNS servers: ${e.message}")
            listOf("8.8.8.8", "1.1.1.1")
        }
    }

    /**
     * Run complete diagnostics in parallel
     */
    suspend fun runParallelDiagnostics(fingerprint: NetworkFingerprint): DiagnosticResult {
        return withContext(Dispatchers.IO) {
            val results = listOf(
                async { runPingTests(fingerprint) },
                async { runTraceroute(fingerprint) },
                async { runSpeedTest(fingerprint) }
            ).awaitAll()

            val pingResults = results[0] as PingResults
            val tracerouteResults = results[1] as TracerouteResults
            val speedtestResults = results[2] as SpeedtestResults

            val (diagnosis, recommendations) = analyzeResults(
                fingerprint,
                pingResults,
                tracerouteResults,
                speedtestResults
            )

            DiagnosticResult(
                timestamp = System.currentTimeMillis(),
                fingerprint = fingerprint,
                pingResults = pingResults,
                tracerouteResults = tracerouteResults,
                speedtestResults = speedtestResults,
                diagnosis = diagnosis,
                recommendations = recommendations
            )
        }
    }

    /**
     * Advanced ping engine with 1400-byte payload
     */
    private suspend fun runPingTests(fingerprint: NetworkFingerprint): PingResults {
        return withContext(Dispatchers.IO) {
            val targets = mapOf(
                "gateway" to fingerprint.gateway,
                "dns" to fingerprint.dns.first(),
                "google" to "8.8.8.8"
            )

            val pingResults = mutableMapOf<String, Pair<Double, Double>>() // loss %, latency ms

            targets.forEach { (name, target) ->
                try {
                    val (loss, avgLatency) = executePing(target)
                    pingResults[name] = Pair(loss, avgLatency)
                } catch (e: Exception) {
                    Log.e(TAG, "Ping failed to $name ($target): ${e.message}")
                    pingResults[name] = Pair(100.0, Double.NaN)
                }
            }

            val jitter = calculateJitter(listOf(
                pingResults["gateway"]?.second ?: 0.0,
                pingResults["dns"]?.second ?: 0.0,
                pingResults["google"]?.second ?: 0.0
            ))

            PingResults(
                gatewayLoss = pingResults["gateway"]?.first ?: 100.0,
                gatewayLatency = pingResults["gateway"]?.second ?: Double.NaN,
                dnsLoss = pingResults["dns"]?.first ?: 100.0,
                dnsLatency = pingResults["dns"]?.second ?: Double.NaN,
                googleLoss = pingResults["google"]?.first ?: 100.0,
                googleLatency = pingResults["google"]?.second ?: Double.NaN,
                jitter = jitter
            )
        }
    }

    private fun executePing(target: String, count: Int = 20, payloadSize: Int = 1400): Pair<Double, Double> {
        return try {
            val runtime = Runtime.getRuntime()
            val command = if (payloadSize > 0) {
                "ping -c $count -s $payloadSize $target"
            } else {
                "ping -c $count $target"
            }

            val process = runtime.exec(command)
            val exitCode = process.waitFor()
            val output = process.inputStream.bufferedReader().readText()

            val loss = extractPacketLoss(output)
            val avgLatency = extractAvgLatency(output)

            Pair(loss, avgLatency)
        } catch (e: Exception) {
            throw e
        }
    }

    private fun extractPacketLoss(output: String): Double {
        val lossPattern = "([0-9]+)\\.?(?:[0-9]*)% packet loss".toRegex()
        val match = lossPattern.find(output)
        return match?.groupValues?.get(1)?.toDoubleOrNull() ?: 100.0
    }

    private fun extractAvgLatency(output: String): Double {
        val latencyPattern = "rtt min/avg/max/mdev = [0-9.]+/([0-9.]+)/[0-9.]+/[0-9.]+ ms".toRegex()
        val match = latencyPattern.find(output)
        return match?.groupValues?.get(1)?.toDoubleOrNull() ?: Double.NaN
    }

    private fun calculateJitter(latencies: List<Double>): Double {
        val validLatencies = latencies.filter { !it.isNaN() && it > 0 }
        if (validLatencies.size < 2) return 0.0

        var totalJitter = 0.0
        for (i in 1 until validLatencies.size) {
            totalJitter += Math.abs(validLatencies[i] - validLatencies[i - 1])
        }

        return totalJitter / (validLatencies.size - 1)
    }

    /**
     * Traceroute implementation
     */
    private suspend fun runTraceroute(fingerprint: NetworkFingerprint): TracerouteResults {
        return withContext(Dispatchers.IO) {
            val hops = mutableListOf<Hop>()
            val latencySpikes = mutableListOf<Int>()
            var firstLossHop = -1

            try {
                val runtime = Runtime.getRuntime()
                val process = runtime.exec("traceroute -I 8.8.8.8") // ICMP traceroute
                val output = process.inputStream.bufferedReader().readText()

                val lines = output.split("\n")
                lines.forEach { line ->
                    if (line.isNotEmpty() && line.first().isDigit()) {
                        val parts = line.split(" ").filter { it.isNotEmpty() }
                        if (parts.size >= 2) {
                            val hopNumber = parts[0].toInt()
                            var ip = "Unknown"
                            var latency = Double.NaN

                            if (parts.size > 2 && !parts[1].contains("*")) {
                                ip = parts[1]
                                if (parts.size > 3) {
                                    val timeStr = parts[2].replace("ms", "")
                                    latency = timeStr.toDoubleOrNull() ?: Double.NaN
                                }
                            }

                            hops.add(Hop(hopNumber, ip, latency))

                            if (latency.isNaN() && firstLossHop == -1) {
                                firstLossHop = hopNumber
                            }

                            if (!latency.isNaN() && hops.size > 1) {
                                val previousLatency = hops[hopNumber - 2].latency
                                if (!previousLatency.isNaN() && latency > previousLatency * 2) {
                                    latencySpikes.add(hopNumber)
                                }
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Traceroute failed: ${e.message}")
            }

            TracerouteResults(hops, firstLossHop, latencySpikes)
        }
    }

    /**
     * Speed test implementation
     */
    private suspend fun runSpeedTest(fingerprint: NetworkFingerprint): SpeedtestResults {
        return withContext(Dispatchers.IO) {
            try {
                // Simple speed test by downloading a test file
                val testUrl = URL("https://speed.hetzner.de/100MB.bin")
                val startTime = System.currentTimeMillis()

                val connection = testUrl.openConnection()
                connection.connectTimeout = 10000
                connection.readTimeout = 30000
                connection.connect()

                val contentLength = connection.contentLength.toDouble()
                val inputStream = connection.getInputStream()
                val buffer = ByteArray(8192)
                var totalBytesRead = 0

                while (true) {
                    val bytesRead = inputStream.read(buffer)
                    if (bytesRead == -1) break
                    totalBytesRead += bytesRead
                }

                val endTime = System.currentTimeMillis()
                val duration = (endTime - startTime).toDouble() / 1000.0 // seconds

                if (duration > 0) {
                    val downloadSpeed = (totalBytesRead * 8) / (duration * 1000000.0) // Mbps
                    val consistency = calculateConsistency(totalBytesRead, duration)

                    SpeedtestResults(
                        downloadSpeed = downloadSpeed,
                        uploadSpeed = 0.0, // Upload test not implemented in this version
                        latency = measureLatency("8.8.8.8"),
                        consistency = consistency
                    )
                } else {
                    SpeedtestResults(0.0, 0.0, Double.NaN, 0.0)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Speed test failed: ${e.message}")
                SpeedtestResults(0.0, 0.0, Double.NaN, 0.0)
            }
        }
    }

    private fun measureLatency(target: String, count: Int = 5): Double {
        val latencies = mutableListOf<Double>()

        repeat(count) {
            val startTime = System.currentTimeMillis()
            try {
                Socket(target, 80).close()
                val endTime = System.currentTimeMillis()
                latencies.add((endTime - startTime).toDouble())
            } catch (e: Exception) {
                Log.e(TAG, "Latency measurement failed: ${e.message}")
            }
        }

        return if (latencies.isNotEmpty()) {
            latencies.average()
        } else {
            Double.NaN
        }
    }

    private fun calculateConsistency(totalBytesRead: Int, duration: Double): Double {
        if (duration <= 0) return 0.0
        return minOf((totalBytesRead * 100.0) / (duration * 1000000), 100.0)
    }

    /**
     * Intelligent analysis engine
     */
    private fun analyzeResults(
        fingerprint: NetworkFingerprint,
        ping: PingResults,
        traceroute: TracerouteResults,
        speedtest: SpeedtestResults
    ): Pair<String, List<String>> {
        val issues = mutableListOf<String>()
        val recommendations = mutableListOf<String>()

        // Analyze ping results
        if (ping.gatewayLoss > 5) {
            issues.add("High packet loss ($ping.gatewayLoss%) to gateway")
            recommendations.add("Check physical connection to router/modem")
        }

        if (ping.gatewayLatency > 100) {
            issues.add("High gateway latency ($ping.gatewayLatency ms)")
            recommendations.add("Consider restarting your router/modem")
        }

        if (ping.jitter > 50) {
            issues.add("High network jitter ($ping.jitter ms)")
            recommendations.add("Use wired connection for critical applications")
        }

        // Analyze traceroute results
        if (traceroute.firstLossHop > 0) {
            issues.add("Packet loss starts at hop ${traceroute.firstLossHop}")
            recommendations.add("Contact your ISP for upstream connectivity issues")
        }

        if (traceroute.latencySpikes.isNotEmpty()) {
            val spikes = traceroute.latencySpikes.joinToString(", ")
            issues.add("Latency spikes detected at hops: $spikes")
            recommendations.add("Monitor for routing instability")
        }

        // Analyze speed test results
        if (speedtest.downloadSpeed < 10) {
            issues.add("Slow download speed (${String.format("%.1f", speedtest.downloadSpeed)} Mbps)")
            recommendations.add("Check for bandwidth-hungry applications or devices")
        }

        if (speedtest.consistency < 70) {
            issues.add("Inconsistent connection quality")
            recommendations.add("Check for Wi-Fi interference or modem issues")
        }

        // Generate diagnosis
        val diagnosis = if (issues.isEmpty()) {
            "Sunya Networking diagnostics completed without finding major issues. " +
                    "Network performance appears to be within normal parameters."
        } else {
            "Sunya Networking has identified several potential network issues:\n" +
                    issues.joinToString("\n") { "- $it" }
        }

        // Add general recommendations if none specific
        if (recommendations.isEmpty()) {
            recommendations.addAll(listOf(
                "Network is functioning normally",
                "Monitor for any future connectivity changes"
            ))
        }

        return Pair(diagnosis, recommendations)
    }
}