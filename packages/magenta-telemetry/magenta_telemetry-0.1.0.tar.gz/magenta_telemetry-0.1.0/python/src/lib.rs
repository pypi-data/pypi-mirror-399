//! Magenta Telemetry Format - Python Bindings
//!
//! Provides Python API for MTF format using PyO3.

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use magenta_telemetry_core as core;

/// Python wrapper for TelemetryData
#[pyclass]
#[derive(Clone)]
struct TelemetryData {
    inner: core::TelemetryData,
}

#[pymethods]
impl TelemetryData {
    #[new]
    #[pyo3(signature = (device_id, uuid, timestamp, sequence_number))]
    fn new(device_id: String, uuid: String, timestamp: i64, sequence_number: u32) -> PyResult<Self> {
        let uuid_bytes = parse_uuid(&uuid)?;
        
        Ok(Self {
            inner: core::TelemetryData::new(device_id, uuid_bytes, timestamp, sequence_number),
        })
    }

    // Getters
    #[getter]
    fn device_id(&self) -> String {
        self.inner.device_id.clone()
    }

    #[getter]
    fn uuid(&self) -> String {
        format_uuid(&self.inner.uuid)
    }

    #[getter]
    fn timestamp(&self) -> i64 {
        self.inner.timestamp
    }

    #[getter]
    fn sequence_number(&self) -> u32 {
        self.inner.sequence_number
    }

    #[getter]
    fn cpu_usage_percent(&self) -> Option<u8> {
        self.inner.cpu_usage_percent
    }

    #[getter]
    fn cpu_temperature(&self) -> Option<f32> {
        self.inner.cpu_temperature
    }

    #[getter]
    fn cpu_frequency(&self) -> Option<u32> {
        self.inner.cpu_frequency
    }

    #[getter]
    fn memory_total(&self) -> Option<u64> {
        self.inner.memory_total
    }

    #[getter]
    fn memory_used(&self) -> Option<u64> {
        self.inner.memory_used
    }

    #[getter]
    fn memory_available(&self) -> Option<u64> {
        self.inner.memory_available
    }

    #[getter]
    fn swap_total(&self) -> Option<u64> {
        self.inner.swap_total
    }

    #[getter]
    fn swap_used(&self) -> Option<u64> {
        self.inner.swap_used
    }

    #[getter]
    fn disk_total(&self) -> Option<u64> {
        self.inner.disk_total
    }

    #[getter]
    fn disk_used(&self) -> Option<u64> {
        self.inner.disk_used
    }

    #[getter]
    fn disk_read_bytes(&self) -> Option<u64> {
        self.inner.disk_read_bytes
    }

    #[getter]
    fn disk_write_bytes(&self) -> Option<u64> {
        self.inner.disk_write_bytes
    }

    #[getter]
    fn network_rx_bytes(&self) -> Option<u64> {
        self.inner.network_rx_bytes
    }

    #[getter]
    fn network_tx_bytes(&self) -> Option<u64> {
        self.inner.network_tx_bytes
    }

    #[getter]
    fn network_rx_packets(&self) -> Option<u64> {
        self.inner.network_rx_packets
    }

    #[getter]
    fn network_tx_packets(&self) -> Option<u64> {
        self.inner.network_tx_packets
    }

    #[getter]
    fn uptime_seconds(&self) -> Option<u64> {
        self.inner.uptime_seconds
    }

    #[getter]
    fn is_proxied(&self) -> bool {
        self.inner.is_proxied
    }

    #[getter]
    fn is_delta(&self) -> bool {
        self.inner.is_delta
    }

    // Setters
    #[setter]
    fn set_cpu_usage_percent(&mut self, value: Option<u8>) {
        self.inner.cpu_usage_percent = value;
    }

    #[setter]
    fn set_cpu_temperature(&mut self, value: Option<f32>) {
        self.inner.cpu_temperature = value;
    }

    #[setter]
    fn set_cpu_frequency(&mut self, value: Option<u32>) {
        self.inner.cpu_frequency = value;
    }

    #[setter]
    fn set_memory_total(&mut self, value: Option<u64>) {
        self.inner.memory_total = value;
    }

    #[setter]
    fn set_memory_used(&mut self, value: Option<u64>) {
        self.inner.memory_used = value;
    }

    #[setter]
    fn set_memory_available(&mut self, value: Option<u64>) {
        self.inner.memory_available = value;
    }

    #[setter]
    fn set_swap_total(&mut self, value: Option<u64>) {
        self.inner.swap_total = value;
    }

    #[setter]
    fn set_swap_used(&mut self, value: Option<u64>) {
        self.inner.swap_used = value;
    }

    #[setter]
    fn set_disk_total(&mut self, value: Option<u64>) {
        self.inner.disk_total = value;
    }

    #[setter]
    fn set_disk_used(&mut self, value: Option<u64>) {
        self.inner.disk_used = value;
    }

    #[setter]
    fn set_disk_read_bytes(&mut self, value: Option<u64>) {
        self.inner.disk_read_bytes = value;
    }

    #[setter]
    fn set_disk_write_bytes(&mut self, value: Option<u64>) {
        self.inner.disk_write_bytes = value;
    }

    #[setter]
    fn set_network_rx_bytes(&mut self, value: Option<u64>) {
        self.inner.network_rx_bytes = value;
    }

    #[setter]
    fn set_network_tx_bytes(&mut self, value: Option<u64>) {
        self.inner.network_tx_bytes = value;
    }

    #[setter]
    fn set_network_rx_packets(&mut self, value: Option<u64>) {
        self.inner.network_rx_packets = value;
    }

    #[setter]
    fn set_network_tx_packets(&mut self, value: Option<u64>) {
        self.inner.network_tx_packets = value;
    }

    #[setter]
    fn set_uptime_seconds(&mut self, value: Option<u64>) {
        self.inner.uptime_seconds = value;
    }

    #[setter]
    fn set_is_proxied(&mut self, value: bool) {
        self.inner.is_proxied = value;
    }

    fn __repr__(&self) -> String {
        format!(
            "TelemetryData(device_id='{}', timestamp={}, seq={})",
            self.inner.device_id, self.inner.timestamp, self.inner.sequence_number
        )
    }
}

/// Encode telemetry data to MTF binary format
#[pyfunction]
#[pyo3(signature = (data, compression=None))]
fn encode(py: Python, data: &TelemetryData, compression: Option<String>) -> PyResult<Py<PyBytes>> {
    let mut inner = data.inner.clone();
    
    inner.compression_type = match compression.as_deref() {
        Some("lz4") => core::CompressionType::Lz4,
        Some("none") | None => core::CompressionType::None,
        Some(other) => {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Unknown compression type: {}", other)
            ));
        }
    };

    let bytes = core::encode(&inner)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

    Ok(PyBytes::new(py, &bytes).into())
}

/// Decode MTF binary format to telemetry data
#[pyfunction]
fn decode(bytes: &[u8]) -> PyResult<TelemetryData> {
    let inner = core::decode(bytes)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

    Ok(TelemetryData { inner })
}

/// Compute delta between two telemetry snapshots
#[pyfunction]
fn compute_delta(previous: &TelemetryData, current: &TelemetryData) -> TelemetryData {
    let delta_inner = core::compute_delta(&previous.inner, &current.inner);
    TelemetryData { inner: delta_inner }
}

/// Apply delta to base snapshot
#[pyfunction]
fn apply_delta(base: &TelemetryData, delta: &TelemetryData) -> TelemetryData {
    let result_inner = core::apply_delta(&base.inner, &delta.inner);
    TelemetryData { inner: result_inner }
}

/// Create sample telemetry data for testing
#[pyfunction]
fn sample() -> TelemetryData {
    TelemetryData {
        inner: core::TelemetryData::sample(),
    }
}

// Helper functions

fn parse_uuid(uuid_str: &str) -> PyResult<[u8; 16]> {
    let clean = uuid_str.replace("-", "");
    
    if clean.len() != 32 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Invalid UUID format"
        ));
    }

    let mut bytes = [0u8; 16];
    for i in 0..16 {
        let byte_str = &clean[i * 2..i * 2 + 2];
        bytes[i] = u8::from_str_radix(byte_str, 16)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid hex in UUID"))?;
    }

    Ok(bytes)
}

fn format_uuid(uuid: &[u8; 16]) -> String {
    format!(
        "{:02x}{:02x}{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}",
        uuid[0], uuid[1], uuid[2], uuid[3],
        uuid[4], uuid[5],
        uuid[6], uuid[7],
        uuid[8], uuid[9],
        uuid[10], uuid[11], uuid[12], uuid[13], uuid[14], uuid[15]
    )
}

/// Python module
#[pymodule]
fn magenta_telemetry(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<TelemetryData>()?;
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(decode, m)?)?;
    m.add_function(wrap_pyfunction!(compute_delta, m)?)?;
    m.add_function(wrap_pyfunction!(apply_delta, m)?)?;
    m.add_function(wrap_pyfunction!(sample, m)?)?;
    
    m.add("__version__", "0.1.0")?;
    
    Ok(())
}
