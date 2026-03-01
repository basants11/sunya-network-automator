package com.sunya.networking

import android.app.job.JobParameters
import android.app.job.JobService
import android.content.Context
import android.content.Intent
import android.os.PersistableBundle
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

private const val TAG = "SunyaBackgroundService"

class SunyaBackgroundService : JobService() {
    private val serviceScope = CoroutineScope(Dispatchers.IO)
    private lateinit var sunyaCore: SunyaCore

    override fun onCreate() {
        super.onCreate()
        sunyaCore = SunyaCore(applicationContext)
    }

    override fun onStartJob(params: JobParameters): Boolean {
        Log.d(TAG, "Job started")

        serviceScope.launch {
            try {
                // Generate network fingerprint
                val fingerprint = sunyaCore.generateNetworkFingerprint()
                if (fingerprint == null) {
                    Log.e(TAG, "Failed to generate network fingerprint")
                    jobFinished(params, false)
                    return@launch
                }

                // Check if we've already tested this network recently
                if (hasRecentTest(fingerprint)) {
                    Log.d(TAG, "Recent test detected, skipping diagnostics")
                    jobFinished(params, false)
                    return@launch
                }

                // Run diagnostics
                Log.d(TAG, "Running diagnostics...")
                val result = sunyaCore.runParallelDiagnostics(fingerprint)

                // Save results to database
                Log.d(TAG, "Saving results to database...")
                val dao = DiagnosticDatabase.getDatabase(applicationContext).diagnosticDao()
                val entity = DiagnosticEntity(
                    timestamp = result.timestamp,
                    networkType = result.fingerprint.interfaceType,
                    ssid = result.fingerprint.ssid,
                    localIp = result.fingerprint.localIp,
                    gateway = result.fingerprint.gateway,
                    dns = result.fingerprint.dns.joinToString(","),
                    avgLatency = result.pingResults.gatewayLatency,
                    packetLoss = result.pingResults.gatewayLoss,
                    downloadSpeed = result.speedtestResults.downloadSpeed,
                    uploadSpeed = result.speedtestResults.uploadSpeed,
                    jitter = result.pingResults.jitter,
                    diagnosis = result.diagnosis,
                    recommendations = result.recommendations.joinToString("\n"),
                    reportPath = generateReportPath(result.timestamp)
                )
                dao.insert(entity)

                // Generate PDF report
                Log.d(TAG, "Generating PDF report...")
                val reportGenerator = ReportGenerator(applicationContext)
                reportGenerator.generatePDFReport(result, entity.reportPath)

                Log.d(TAG, "Diagnostics completed successfully")
                updateLastTestTime(fingerprint)

            } catch (e: Exception) {
                Log.e(TAG, "Error during diagnostics: ${e.message}", e)
            }

            jobFinished(params, false)
        }

        return true // Job continues running in coroutine
    }

    override fun onStopJob(params: JobParameters): Boolean {
        Log.d(TAG, "Job stopped")
        serviceScope.cancel()
        return true // Retry the job if it was stopped prematurely
    }

    private fun hasRecentTest(fingerprint: SunyaCore.NetworkFingerprint): Boolean {
        val sharedPrefs = getSharedPreferences("sunya_prefs", Context.MODE_PRIVATE)
        val lastTestKey = generateFingerprintKey(fingerprint)
        val lastTestTime = sharedPrefs.getLong(lastTestKey, 0L)
        val currentTime = System.currentTimeMillis()

        // Skip if tested within last 30 minutes
        return (currentTime - lastTestTime) < 30 * 60 * 1000
    }

    private fun updateLastTestTime(fingerprint: SunyaCore.NetworkFingerprint) {
        val sharedPrefs = getSharedPreferences("sunya_prefs", Context.MODE_PRIVATE)
        val lastTestKey = generateFingerprintKey(fingerprint)
        sharedPrefs.edit()
            .putLong(lastTestKey, System.currentTimeMillis())
            .apply()
    }

    private fun generateFingerprintKey(fingerprint: SunyaCore.NetworkFingerprint): String {
        return "test_${fingerprint.interfaceType}_${fingerprint.gateway}"
    }

    private fun generateReportPath(timestamp: Long): String {
        val reportDir = applicationContext.getExternalFilesDir(null)?.absolutePath
            ?: applicationContext.filesDir.absolutePath
        return "$reportDir/SUNYA_Network_Report_${timestamp}.pdf"
    }

    companion object {
        private const val JOB_ID = 1001

        fun enqueueWork(context: Context) {
            val jobScheduler = context.getSystemService(Context.JOB_SCHEDULER_SERVICE) as android.app.job.JobScheduler
            val jobInfo = android.app.job.JobInfo.Builder(JOB_ID, android.content.ComponentName(context, SunyaBackgroundService::class.java))
                .setRequiredNetworkType(android.app.job.JobInfo.NETWORK_TYPE_ANY)
                .setPersisted(true)
                .setMinimumLatency(1000 * 60) // Delay 1 minute before starting
                .setOverrideDeadline(1000 * 60 * 10) // Must start within 10 minutes
                .build()

            jobScheduler.schedule(jobInfo)
            Log.d(TAG, "Background service scheduled")
        }
    }
}