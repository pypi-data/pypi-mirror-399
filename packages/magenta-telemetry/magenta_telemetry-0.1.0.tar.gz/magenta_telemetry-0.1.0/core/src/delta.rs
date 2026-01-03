//! Magenta Telemetry Format - Delta Encoding
//!
//! Implements delta encoding to transmit only changed fields.

use crate::types::TelemetryData;

/// Compute delta between two telemetry snapshots
/// Returns a new TelemetryData with only changed fields set
pub fn compute_delta(previous: &TelemetryData, current: &TelemetryData) -> TelemetryData {
    let mut delta = TelemetryData::new(
        current.device_id.clone(),
        current.uuid,
        current.timestamp,
        current.sequence_number,
    );

    delta.compression_type = current.compression_type;
    delta.is_proxied = current.is_proxied;
    delta.is_delta = true; // Mark as delta

    // Only include fields that changed
    if current.cpu_usage_percent != previous.cpu_usage_percent {
        delta.cpu_usage_percent = current.cpu_usage_percent;
    }

    if current.cpu_temperature != previous.cpu_temperature {
        delta.cpu_temperature = current.cpu_temperature;
    }

    if current.cpu_frequency != previous.cpu_frequency {
        delta.cpu_frequency = current.cpu_frequency;
    }

    if current.memory_total != previous.memory_total {
        delta.memory_total = current.memory_total;
    }

    if current.memory_used != previous.memory_used {
        delta.memory_used = current.memory_used;
    }

    if current.memory_available != previous.memory_available {
        delta.memory_available = current.memory_available;
    }

    if current.swap_total != previous.swap_total {
        delta.swap_total = current.swap_total;
    }

    if current.swap_used != previous.swap_used {
        delta.swap_used = current.swap_used;
    }

    if current.disk_total != previous.disk_total {
        delta.disk_total = current.disk_total;
    }

    if current.disk_used != previous.disk_used {
        delta.disk_used = current.disk_used;
    }

    if current.disk_read_bytes != previous.disk_read_bytes {
        delta.disk_read_bytes = current.disk_read_bytes;
    }

    if current.disk_write_bytes != previous.disk_write_bytes {
        delta.disk_write_bytes = current.disk_write_bytes;
    }

    if current.network_rx_bytes != previous.network_rx_bytes {
        delta.network_rx_bytes = current.network_rx_bytes;
    }

    if current.network_tx_bytes != previous.network_tx_bytes {
        delta.network_tx_bytes = current.network_tx_bytes;
    }

    if current.network_rx_packets != previous.network_rx_packets {
        delta.network_rx_packets = current.network_rx_packets;
    }

    if current.network_tx_packets != previous.network_tx_packets {
        delta.network_tx_packets = current.network_tx_packets;
    }

    if current.uptime_seconds != previous.uptime_seconds {
        delta.uptime_seconds = current.uptime_seconds;
    }

    delta
}

/// Apply delta to a base snapshot to reconstruct full state
pub fn apply_delta(base: &TelemetryData, delta: &TelemetryData) -> TelemetryData {
    let mut result = base.clone();

    // Update metadata
    result.timestamp = delta.timestamp;
    result.sequence_number = delta.sequence_number;
    result.is_proxied = delta.is_proxied;

    // Apply changed fields
    if delta.cpu_usage_percent.is_some() {
        result.cpu_usage_percent = delta.cpu_usage_percent;
    }

    if delta.cpu_temperature.is_some() {
        result.cpu_temperature = delta.cpu_temperature;
    }

    if delta.cpu_frequency.is_some() {
        result.cpu_frequency = delta.cpu_frequency;
    }

    if delta.memory_total.is_some() {
        result.memory_total = delta.memory_total;
    }

    if delta.memory_used.is_some() {
        result.memory_used = delta.memory_used;
    }

    if delta.memory_available.is_some() {
        result.memory_available = delta.memory_available;
    }

    if delta.swap_total.is_some() {
        result.swap_total = delta.swap_total;
    }

    if delta.swap_used.is_some() {
        result.swap_used = delta.swap_used;
    }

    if delta.disk_total.is_some() {
        result.disk_total = delta.disk_total;
    }

    if delta.disk_used.is_some() {
        result.disk_used = delta.disk_used;
    }

    if delta.disk_read_bytes.is_some() {
        result.disk_read_bytes = delta.disk_read_bytes;
    }

    if delta.disk_write_bytes.is_some() {
        result.disk_write_bytes = delta.disk_write_bytes;
    }

    if delta.network_rx_bytes.is_some() {
        result.network_rx_bytes = delta.network_rx_bytes;
    }

    if delta.network_tx_bytes.is_some() {
        result.network_tx_bytes = delta.network_tx_bytes;
    }

    if delta.network_rx_packets.is_some() {
        result.network_rx_packets = delta.network_rx_packets;
    }

    if delta.network_tx_packets.is_some() {
        result.network_tx_packets = delta.network_tx_packets;
    }

    if delta.uptime_seconds.is_some() {
        result.uptime_seconds = delta.uptime_seconds;
    }

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_delta_no_changes() {
        let data1 = TelemetryData::sample();
        let data2 = data1.clone();

        let delta = compute_delta(&data1, &data2);
        
        // Only metadata should be present, no metric fields
        assert!(delta.is_delta);
        assert!(delta.cpu_usage_percent.is_none());
        assert!(delta.memory_used.is_none());
    }

    #[test]
    fn test_compute_delta_some_changes() {
        let data1 = TelemetryData::sample();
        let mut data2 = data1.clone();
        
        data2.cpu_usage_percent = Some(75);
        data2.memory_used = Some(9999999999);
        data2.timestamp = 1735686700000;
        data2.sequence_number = 43;

        let delta = compute_delta(&data1, &data2);
        
        assert!(delta.is_delta);
        assert_eq!(delta.cpu_usage_percent, Some(75));
        assert_eq!(delta.memory_used, Some(9999999999));
        assert_eq!(delta.timestamp, 1735686700000);
        assert_eq!(delta.sequence_number, 43);
        
        // Unchanged fields should be None
        assert!(delta.memory_total.is_none());
        assert!(delta.disk_total.is_none());
    }

    #[test]
    fn test_apply_delta() {
        let base = TelemetryData::sample();
        let mut delta = TelemetryData::new(
            base.device_id.clone(),
            base.uuid,
            1735686700000,
            43,
        );
        delta.is_delta = true;
        delta.cpu_usage_percent = Some(88);
        delta.memory_used = Some(12345678901);

        let result = apply_delta(&base, &delta);
        
        // Updated fields
        assert_eq!(result.cpu_usage_percent, Some(88));
        assert_eq!(result.memory_used, Some(12345678901));
        assert_eq!(result.timestamp, 1735686700000);
        assert_eq!(result.sequence_number, 43);
        
        // Unchanged fields preserved
        assert_eq!(result.memory_total, base.memory_total);
        assert_eq!(result.disk_total, base.disk_total);
        assert_eq!(result.cpu_temperature, base.cpu_temperature);
    }

    #[test]
    fn test_delta_roundtrip() {
        let snapshot1 = TelemetryData::sample();
        let mut snapshot2 = snapshot1.clone();
        
        snapshot2.cpu_usage_percent = Some(99);
        snapshot2.timestamp += 1000;
        snapshot2.sequence_number += 1;

        let delta = compute_delta(&snapshot1, &snapshot2);
        let reconstructed = apply_delta(&snapshot1, &delta);
        
        assert_eq!(reconstructed.cpu_usage_percent, snapshot2.cpu_usage_percent);
        assert_eq!(reconstructed.timestamp, snapshot2.timestamp);
        assert_eq!(reconstructed.sequence_number, snapshot2.sequence_number);
    }
}
