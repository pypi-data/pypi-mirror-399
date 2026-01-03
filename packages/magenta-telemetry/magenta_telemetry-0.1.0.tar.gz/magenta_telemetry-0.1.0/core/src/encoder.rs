//! Magenta Telemetry Format - Binary Encoder
//!
//! Encodes TelemetryData into the MTF binary format.

use crate::types::{CompressionType, FieldId, TelemetryData, TypeId};
use crate::compression;

const VERSION: u8 = 0x01;

/// Encode telemetry data into MTF binary format
pub fn encode(data: &TelemetryData) -> Result<Vec<u8>, String> {
    let mut buffer = Vec::with_capacity(256);

    // Encode header (15 bytes)
    encode_header(data, &mut buffer)?;

    // Encode variable data
    let variable_start = buffer.len();
    
    // Device ID
    buffer.extend_from_slice(data.device_id.as_bytes());
    
    // UUID
    buffer.extend_from_slice(&data.uuid);
    
    // Payload (field-encoded data)
    let payload = encode_payload(data)?;
    
    // Apply compression if requested
    let final_payload = if data.compression_type == CompressionType::Lz4 {
        compression::compress_lz4(&payload)?
    } else {
        payload
    };
    
    buffer.extend_from_slice(&final_payload);

    // Compute and append checksum (CRC32)
    let checksum = compute_checksum(&buffer);
    buffer.extend_from_slice(&checksum.to_le_bytes());

    Ok(buffer)
}

/// Encode the 15-byte header
fn encode_header(data: &TelemetryData, buffer: &mut Vec<u8>) -> Result<(), String> {
    // Validate device ID length
    if data.device_id.len() > 255 {
        return Err("Device ID too long (max 255 bytes)".to_string());
    }

    // Version (1 byte)
    buffer.push(VERSION);

    // Flags (1 byte)
    let flags = encode_flags(data);
    buffer.push(flags);

    // Timestamp (8 bytes, little-endian)
    buffer.extend_from_slice(&data.timestamp.to_le_bytes());

    // Sequence number (4 bytes, little-endian)
    buffer.extend_from_slice(&data.sequence_number.to_le_bytes());

    // Device ID length (1 byte)
    buffer.push(data.device_id.len() as u8);

    Ok(())
}

/// Encode flags byte
fn encode_flags(data: &TelemetryData) -> u8 {
    let mut flags = 0u8;

    // Compression type (bits 7-5)
    flags |= data.compression_type.to_bits() << 5;

    // Delta encoding (bit 4)
    if data.is_delta {
        flags |= 0b0001_0000;
    }

    // Proxied (bit 3)
    if data.is_proxied {
        flags |= 0b0000_1000;
    }

    // Bits 2-0 reserved (must be 0)
    flags
}

/// Encode payload (field-encoded telemetry)
fn encode_payload(data: &TelemetryData) -> Result<Vec<u8>, String> {
    let mut payload = Vec::with_capacity(128);

    // Encode each field
    if let Some(val) = data.cpu_usage_percent {
        encode_u8_field(&mut payload, FieldId::CpuUsage as u8, val);
    }

    if let Some(val) = data.cpu_temperature {
        encode_f32_field(&mut payload, FieldId::CpuTemp as u8, val);
    }

    if let Some(val) = data.cpu_frequency {
        encode_u32_field(&mut payload, FieldId::CpuFreq as u8, val);
    }

    if let Some(val) = data.memory_total {
        encode_u64_field(&mut payload, FieldId::MemTotal as u8, val);
    }

    if let Some(val) = data.memory_used {
        encode_u64_field(&mut payload, FieldId::MemUsed as u8, val);
    }

    if let Some(val) = data.memory_available {
        encode_u64_field(&mut payload, FieldId::MemAvailable as u8, val);
    }

    if let Some(val) = data.swap_total {
        encode_u64_field(&mut payload, FieldId::SwapTotal as u8, val);
    }

    if let Some(val) = data.swap_used {
        encode_u64_field(&mut payload, FieldId::SwapUsed as u8, val);
    }

    if let Some(val) = data.disk_total {
        encode_u64_field(&mut payload, FieldId::DiskTotal as u8, val);
    }

    if let Some(val) = data.disk_used {
        encode_u64_field(&mut payload, FieldId::DiskUsed as u8, val);
    }

    if let Some(val) = data.disk_read_bytes {
        encode_u64_field(&mut payload, FieldId::DiskReadBytes as u8, val);
    }

    if let Some(val) = data.disk_write_bytes {
        encode_u64_field(&mut payload, FieldId::DiskWriteBytes as u8, val);
    }

    if let Some(val) = data.network_rx_bytes {
        encode_u64_field(&mut payload, FieldId::NetRxBytes as u8, val);
    }

    if let Some(val) = data.network_tx_bytes {
        encode_u64_field(&mut payload, FieldId::NetTxBytes as u8, val);
    }

    if let Some(val) = data.network_rx_packets {
        encode_u64_field(&mut payload, FieldId::NetRxPackets as u8, val);
    }

    if let Some(val) = data.network_tx_packets {
        encode_u64_field(&mut payload, FieldId::NetTxPackets as u8, val);
    }

    if let Some(val) = data.uptime_seconds {
        encode_u64_field(&mut payload, FieldId::UptimeSeconds as u8, val);
    }

    Ok(payload)
}

/// Encode a u8 field
fn encode_u8_field(buffer: &mut Vec<u8>, field_num: u8, value: u8) {
    let field_byte = TypeId::U8.encode_field_byte(field_num);
    buffer.push(field_byte);
    buffer.push(value);
}

/// Encode a u32 field
fn encode_u32_field(buffer: &mut Vec<u8>, field_num: u8, value: u32) {
    let field_byte = TypeId::U32.encode_field_byte(field_num);
    buffer.push(field_byte);
    buffer.extend_from_slice(&value.to_le_bytes());
}

/// Encode a u64 field
fn encode_u64_field(buffer: &mut Vec<u8>, field_num: u8, value: u64) {
    let field_byte = TypeId::U64.encode_field_byte(field_num);
    buffer.push(field_byte);
    buffer.extend_from_slice(&value.to_le_bytes());
}

/// Encode a f32 field
fn encode_f32_field(buffer: &mut Vec<u8>, field_num: u8, value: f32) {
    let field_byte = TypeId::F32.encode_field_byte(field_num);
    buffer.push(field_byte);
    buffer.extend_from_slice(&value.to_le_bytes());
}

/// Compute CRC32 checksum
fn compute_checksum(data: &[u8]) -> u32 {
    crc32fast::hash(data)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encode_sample() {
        let data = TelemetryData::sample();
        let result = encode(&data);
        assert!(result.is_ok());

        let bytes = result.unwrap();
        
        // Check version
        assert_eq!(bytes[0], VERSION);
        
        // Minimum size check (header + device_id + uuid + some payload + checksum)
        assert!(bytes.len() > 50);
    }

    #[test]
    fn test_encode_with_compression() {
        let mut data = TelemetryData::sample();
        data.compression_type = CompressionType::Lz4;
        
        let result = encode(&data);
        assert!(result.is_ok());

        let bytes = result.unwrap();
        
        // Check flags contain compression bit
        let flags = bytes[1];
        let compression_bits = (flags >> 5) & 0b111;
        assert_eq!(compression_bits, 1); // LZ4
    }

    #[test]
    fn test_encode_flags() {
        let mut data = TelemetryData::sample();
        data.compression_type = CompressionType::Lz4;
        data.is_delta = true;
        data.is_proxied = true;

        let flags = encode_flags(&data);
        
        // Compression (bits 7-5): 001
        assert_eq!((flags >> 5) & 0b111, 1);
        
        // Delta (bit 4): 1
        assert_eq!((flags >> 4) & 1, 1);
        
        // Proxied (bit 3): 1
        assert_eq!((flags >> 3) & 1, 1);
    }

    #[test]
    fn test_device_id_too_long() {
        let uuid = [0u8; 16];
        let long_id = "a".repeat(256);
        let data = TelemetryData::new(long_id, uuid, 1234567890, 1);
        
        let result = encode(&data);
        assert!(result.is_err());
    }

    #[test]
    fn test_minimal_packet() {
        let uuid = [0u8; 16];
        let data = TelemetryData::new("test".to_string(), uuid, 1000, 1);
        
        let result = encode(&data);
        assert!(result.is_ok());

        let bytes = result.unwrap();
        
        // Header (15) + device_id (4) + uuid (16) + checksum (4) = 39 minimum
        assert!(bytes.len() >= 39);
    }
}
