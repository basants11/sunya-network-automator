package com.sunya.networking

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.graphics.pdf.PdfDocument
import android.os.Environment
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private const val TAG = "ReportGenerator"

class ReportGenerator(private val context: Context) {

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())

    fun generatePDFReport(result: SunyaCore.DiagnosticResult, outputPath: String): Boolean {
        return try {
            Log.d(TAG, "Generating PDF report at: $outputPath")

            val document = PdfDocument()
            var pageNumber = 1

            // Cover Page
            addCoverPage(document, result)

            // Network Fingerprint Page
            addFingerprintPage(document, result.fingerprint)

            // Ping Results
            addPingResultsPage(document, result.pingResults)

            // Traceroute Results
            addTraceroutePage(document, result.tracerouteResults)

            // Speed Test Results
            addSpeedtestPage(document, result.speedtestResults)

            // Analysis & Recommendations
            addAnalysisPage(document, result.diagnosis, result.recommendations)

            // Save document
            val outputStream = FileOutputStream(File(outputPath))
            document.writeTo(outputStream)
            document.close()
            outputStream.close()

            Log.d(TAG, "PDF report generated successfully")
            true
        } catch (e: Exception) {
            Log.e(TAG, "PDF generation failed: ${e.message}", e)
            false
        }
    }

    private fun addCoverPage(document: PdfDocument, result: SunyaCore.DiagnosticResult) {
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 1).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        // Title
        val titlePaint = Paint()
        titlePaint.color = Color.BLACK
        titlePaint.textSize = 36f
        titlePaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Sunya Networking", 50f, 100f, titlePaint)

        // Subtitle
        val subtitlePaint = Paint()
        subtitlePaint.color = Color.GRAY
        subtitlePaint.textSize = 16f
        canvas.drawText("Professional Network Automation & Diagnostics Suite", 50f, 130f, subtitlePaint)

        // Report Details
        val detailsPaint = Paint()
        detailsPaint.color = Color.BLACK
        detailsPaint.textSize = 14f

        var yPosition = 200f
        canvas.drawText("Report Generated: ${dateFormat.format(Date(result.timestamp))}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Network Type: ${result.fingerprint.interfaceType}", 50f, yPosition, detailsPaint)
        yPosition += 20f

        if (result.fingerprint.ssid != null) {
            canvas.drawText("SSID: ${result.fingerprint.ssid}", 50f, yPosition, detailsPaint)
            yPosition += 20f
        }

        if (result.fingerprint.mobileNetwork != null) {
            canvas.drawText("Network: ${result.fingerprint.mobileNetwork}", 50f, yPosition, detailsPaint)
            yPosition += 20f
        }

        canvas.drawText("Local IP: ${result.fingerprint.localIp}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Gateway: ${result.fingerprint.gateway}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("DNS: ${result.fingerprint.dns.joinToString(", ")}", 50f, yPosition, detailsPaint)

        // Watermark
        val watermarkPaint = Paint()
        watermarkPaint.color = Color.parseColor("#1a000000")
        watermarkPaint.textSize = 48f
        watermarkPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        watermarkPaint.alpha = 30

        canvas.save()
        canvas.rotate(-30f, 297f, 421f)
        canvas.drawText("Sunya Networking", 100f, 400f, watermarkPaint)
        canvas.restore()

        document.finishPage(page)
    }

    private fun addFingerprintPage(document: PdfDocument, fingerprint: SunyaCore.NetworkFingerprint) {
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 2).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        val headerPaint = Paint()
        headerPaint.color = Color.BLACK
        headerPaint.textSize = 24f
        headerPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Network Fingerprint", 50f, 50f, headerPaint)

        val detailsPaint = Paint()
        detailsPaint.color = Color.BLACK
        detailsPaint.textSize = 14f

        var yPosition = 80f

        canvas.drawText("Interface Type: ${fingerprint.interfaceType}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Local IP Address: ${fingerprint.localIp}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Gateway: ${fingerprint.gateway}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("DNS Servers: ${fingerprint.dns.joinToString(", ")}", 50f, yPosition, detailsPaint)
        yPosition += 20f

        if (fingerprint.ssid != null) {
            canvas.drawText("Wi-Fi SSID: ${fingerprint.ssid}", 50f, yPosition, detailsPaint)
            yPosition += 20f
        }

        if (fingerprint.mobileNetwork != null) {
            canvas.drawText("Mobile Network: ${fingerprint.mobileNetwork}", 50f, yPosition, detailsPaint)
            yPosition += 20f
        }

        canvas.drawText("Time: ${dateFormat.format(Date(fingerprint.timestamp))}", 50f, yPosition, detailsPaint)

        document.finishPage(page)
    }

    private fun addPingResultsPage(document: PdfDocument, pingResults: SunyaCore.PingResults) {
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 3).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        val headerPaint = Paint()
        headerPaint.color = Color.BLACK
        headerPaint.textSize = 24f
        headerPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Ping Test Results", 50f, 50f, headerPaint)

        val detailsPaint = Paint()
        detailsPaint.color = Color.BLACK
        detailsPaint.textSize = 14f

        var yPosition = 80f

        canvas.drawText("Payload Size: 1400 bytes", 50f, yPosition, detailsPaint)
        yPosition += 30f

        canvas.drawText("Gateway:", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("  Packet Loss: ${String.format("%.1f%%", pingResults.gatewayLoss)}", 70f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("  Latency: ${String.format("%.1f ms", pingResults.gatewayLatency)}", 70f, yPosition, detailsPaint)
        yPosition += 30f

        canvas.drawText("DNS Server:", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("  Packet Loss: ${String.format("%.1f%%", pingResults.dnsLoss)}", 70f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("  Latency: ${String.format("%.1f ms", pingResults.dnsLatency)}", 70f, yPosition, detailsPaint)
        yPosition += 30f

        canvas.drawText("Google DNS (8.8.8.8):", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("  Packet Loss: ${String.format("%.1f%%", pingResults.googleLoss)}", 70f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("  Latency: ${String.format("%.1f ms", pingResults.googleLatency)}", 70f, yPosition, detailsPaint)
        yPosition += 30f

        canvas.drawText("Network Jitter: ${String.format("%.1f ms", pingResults.jitter)}", 50f, yPosition, detailsPaint)

        document.finishPage(page)
    }

    private fun addTraceroutePage(document: PdfDocument, tracerouteResults: SunyaCore.TracerouteResults) {
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 4).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        val headerPaint = Paint()
        headerPaint.color = Color.BLACK
        headerPaint.textSize = 24f
        headerPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Traceroute Results", 50f, 50f, headerPaint)

        val detailsPaint = Paint()
        detailsPaint.color = Color.BLACK
        detailsPaint.textSize = 12f

        var yPosition = 80f

        tracerouteResults.hops.forEach { hop ->
            if (yPosition > 780) {
                document.finishPage(page)
                yPosition = 50f
            }

            val hopText = "Hop ${hop.number}: ${hop.ip} (${if (hop.latency.isNaN()) "*" else String.format("%.1f ms", hop.latency)})"
            canvas.drawText(hopText, 50f, yPosition, detailsPaint)
            yPosition += 15f
        }

        if (tracerouteResults.firstLossHop > 0) {
            yPosition += 20f
            canvas.drawText("First Loss Hop: ${tracerouteResults.firstLossHop}", 50f, yPosition, detailsPaint)
        }

        if (tracerouteResults.latencySpikes.isNotEmpty()) {
            yPosition += 20f
            canvas.drawText("Latency Spikes at Hops: ${tracerouteResults.latencySpikes.joinToString(", ")}", 50f, yPosition, detailsPaint)
        }

        document.finishPage(page)
    }

    private fun addSpeedtestPage(document: PdfDocument, speedtestResults: SunyaCore.SpeedtestResults) {
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 5).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        val headerPaint = Paint()
        headerPaint.color = Color.BLACK
        headerPaint.textSize = 24f
        headerPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Speed Test Results", 50f, 50f, headerPaint)

        val detailsPaint = Paint()
        detailsPaint.color = Color.BLACK
        detailsPaint.textSize = 14f

        var yPosition = 80f

        canvas.drawText("Download Speed: ${String.format("%.1f Mbps", speedtestResults.downloadSpeed)}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Upload Speed: ${String.format("%.1f Mbps", speedtestResults.uploadSpeed)}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Latency: ${String.format("%.1f ms", speedtestResults.latency)}", 50f, yPosition, detailsPaint)
        yPosition += 20f
        canvas.drawText("Consistency: ${String.format("%.0f%%", speedtestResults.consistency)}", 50f, yPosition, detailsPaint)

        document.finishPage(page)
    }

    private fun addAnalysisPage(document: PdfDocument, diagnosis: String, recommendations: List<String>) {
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 6).create()
        val page = document.startPage(pageInfo)
        val canvas = page.canvas

        val headerPaint = Paint()
        headerPaint.color = Color.BLACK
        headerPaint.textSize = 24f
        headerPaint.typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        canvas.drawText("Analysis & Recommendations", 50f, 50f, headerPaint)

        val diagnosisPaint = Paint()
        diagnosisPaint.color = Color.BLACK
        diagnosisPaint.textSize = 14f
        diagnosisPaint.textAlign = Paint.Align.LEFT

        val recommendationsPaint = Paint()
        recommendationsPaint.color = Color.BLACK
        recommendationsPaint.textSize = 14f

        var yPosition = 80f

        canvas.drawText("Diagnosis:", 50f, yPosition, diagnosisPaint)
        yPosition += 20f

        // Draw diagnosis with line wrapping
        val diagnosisLines = wrapText(diagnosis, 500f, diagnosisPaint)
        diagnosisLines.forEach { line ->
            canvas.drawText(line, 50f, yPosition, diagnosisPaint)
            yPosition += 20f
        }

        if (recommendations.isNotEmpty()) {
            yPosition += 20f
            canvas.drawText("Recommendations:", 50f, yPosition, recommendationsPaint)
            yPosition += 20f

            recommendations.forEach { recommendation ->
                canvas.drawText("• $recommendation", 70f, yPosition, recommendationsPaint)
                yPosition += 20f
            }
        }

        document.finishPage(page)
    }

    private fun wrapText(text: String, maxWidth: Float, paint: Paint): List<String> {
        val lines = mutableListOf<String>()
        val words = text.split(" ").toMutableList()
        var currentLine = StringBuilder()

        while (words.isNotEmpty()) {
            val word = words.removeAt(0)
            val testLine = if (currentLine.isEmpty()) word else "${currentLine} $word"

            if (paint.measureText(testLine) <= maxWidth) {
                currentLine = StringBuilder(testLine)
            } else {
                lines.add(currentLine.toString())
                currentLine = StringBuilder(word)
            }
        }

        if (currentLine.isNotEmpty()) {
            lines.add(currentLine.toString())
        }

        return lines
    }

    fun shareReport(context: Context, reportPath: String) {
        try {
            val reportFile = File(reportPath)
            if (!reportFile.exists()) {
                Log.e(TAG, "Report file not found: $reportPath")
                return
            }

            val uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                reportFile
            )

            val intent = Intent(Intent.ACTION_SEND)
            intent.type = "application/pdf"
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.putExtra(Intent.EXTRA_SUBJECT, "Sunya Networking Report")
            intent.putExtra(Intent.EXTRA_TEXT, "Network diagnostic report generated by Sunya Networking")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

            context.startActivity(Intent.createChooser(intent, "Share Report"))
        } catch (e: Exception) {
            Log.e(TAG, "Failed to share report: ${e.message}", e)
        }
    }
}