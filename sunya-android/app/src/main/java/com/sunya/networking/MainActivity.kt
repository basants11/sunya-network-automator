package com.sunya.networking

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.sunya.networking.databinding.ActivityMainBinding
import com.sunya.networking.viewmodels.MainViewModel

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        setupObservables()
        checkPermissions()
    }

    private fun setupUI() {
        // Start diagnostic manually
        binding.btnStartDiagnostics.setOnClickListener {
            viewModel.startDiagnostics()
        }

        // View reports
        binding.btnViewReports.setOnClickListener {
            val intent = Intent(this, ReportsActivity::class.java)
            startActivity(intent)
        }

        // Settings
        binding.btnSettings.setOnClickListener {
            val intent = Intent(this, SettingsActivity::class.java)
            startActivity(intent)
        }

        // About
        binding.btnAbout.setOnClickListener {
            showAboutDialog()
        }
    }

    private fun setupObservables() {
        viewModel.isRunning.observe(this) { isRunning ->
            binding.btnStartDiagnostics.isEnabled = !isRunning
            binding.btnStartDiagnostics.text = if (isRunning) "Diagnostics Running..." else "Start Diagnostics"
        }

        viewModel.lastResult.observe(this) { result ->
            result?.let {
                binding.tvLastRun.text = "Last Run: ${it.timestamp}"
                binding.tvNetworkType.text = "Network: ${it.networkType}"
                binding.tvLatency.text = "Latency: ${it.avgLatency}ms"
                binding.tvPacketLoss.text = "Packet Loss: ${it.packetLoss}%"
                binding.tvDownloadSpeed.text = "Download: ${it.downloadSpeed} Mbps"
                binding.tvUploadSpeed.text = "Upload: ${it.uploadSpeed} Mbps"
                binding.tvDiagnosis.text = it.diagnosis
            }
        }

        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, it, Toast.LENGTH_LONG).show()
                viewModel.error.value = null
            }
        }
    }

    private fun checkPermissions() {
        if (!viewModel.hasRequiredPermissions()) {
            viewModel.requestPermissions(this)
        }
    }

    private fun showAboutDialog() {
        val dialog = AboutDialog(this)
        dialog.show()
    }

    override fun onResume() {
        super.onResume()
        viewModel.loadLastResult()
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        viewModel.onRequestPermissionsResult(requestCode, permissions, grantResults)
    }
}