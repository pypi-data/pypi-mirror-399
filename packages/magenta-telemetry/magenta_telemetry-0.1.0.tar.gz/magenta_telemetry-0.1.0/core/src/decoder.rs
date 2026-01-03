//! Magenta Telemetry Format - Binary Decoder
//!
//! Decodes MTF binary format into TelemetryData.

use crate::types::{CompressionType, FieldId, TelemetryData, TypeId};
use crate::compression;

const VERSION: u8 = 0x01;

/// Decode MTF binary format into telemetry data
pub fn decode(bytes: &[u8]) -> Result<TelemetryData, String> {
    if bytes.len() < 19 {
        return Err("Packet too small (minimum 19 bytes)".to_string());
    }

    // Verify checksum
    let data_len = bytes.len() - 4;
    let expected_checksum = u32::from_le_bytes([
        bytes[data_len],
        bytes[data_len + 1],
        bytes[data_len + 2],
        bytes[data_len + 3],
    ]);
    
    let actual_checksum = crc32fast::hash(&bytes[..data_len]);
    if expected_checksum != actual_checksum {
        return Err(format!(
            "Checksum mismatch: expected {:08x}, got {:08x}",
            expected_checksum, actual_checksum
        ));
    }

    // Parse header
    let mut offset = 0;
    let (header, device_id_len) = decode_header(bytes, &mut offset)?;

    // Parse device ID
    if offset + device_id_len > data_len {
        return Err("Invalid device ID length".to_string());
    }
    
    let device_id = String::from_utf8(bytes[offset..offset + device_id_len].to_vec())
        .map_err(|e| format!("Invalid UTF-8 in device ID: {}", e))?;
    offset += device_id_len;

    // Parse UUID
    if offset + 16 > data_len {
        return Err("Packet truncated (missing UUID)".to_string());
    }
    
    let mut uuid = [0u8; 16];
    uuid.copy_from_slice(&bytes[offset..offset + 16]);
    offset += 16;

    // Parse payload
    let payload_bytes = &bytes[offset..data_len];
    
    // Decompress if needed
    let decompressed_payload = if header.compression_type == CompressionType::Lz4 {
        compression::decompress_lz4(payload_bytes)?
    } else {
        payload_bytes.to_vec()
    };

    // Decode fields from payload
    let mut telemetry = TelemetryData::new(
        device_id,
        uuid,
        header.timestamp,
        header.sequence_number,
    );

    telemetry.compression_type = header.compression_type;
    telemetry.is_delta = header.is_delta;
    telemetry.is_proxied = header.is_proxied;

    decode_payload(&decompressed_payload, &mut telemetry)?;

    Ok(telemetry)
}

/// Header information parsed from packet
struct Header {
    timestamp: i64,
    sequence_number: u32,
    compression_type: CompressionType,
    is_delta: bool,
    is_proxied: bool,
}

/// Decode the 15-byte header
fn decode_header(bytes: &[u8], offset: &mut usize) -> Result<(Header, usize), String> {
    // Version
    let version = bytes[0];
    if version != VERSION {
        return Err(format!("Unsupported version: {}", version));
    }

    // Flags
    let flags = bytes[1];
    let compression_bits = (flags >> 5) & 0b111;
    let compression_type = CompressionType::from_bits(compression_bits)?;
    let is_delta = (flags & 0b0001_0000) != 0;
    let is_proxied = (flags & 0b0000_1000) != 0;

    // Timestamp
    let timestamp = i64::from_le_bytes([
        bytes[2], bytes[3], bytes[4], bytes[5],
        bytes[6], bytes[7], bytes[8], bytes[9],
    ]);

    // Sequence number
    let sequence_number = u32::from_le_bytes([
        bytes[10], bytes[11], bytes[12], bytes[13],
    ]);

    // Device ID length
    let device_id_len = bytes[14] as usize;

    *offset = 15;

    Ok((
        Header {
            timestamp,
            sequence_number,
            compression_type,
            is_delta,
            is_proxied,
        },
        device_id_len,
    ))
}

/// Decode payload fields into telemetry data
fn decode_payload(payload: &[u8], telemetry: &mut TelemetryData) -> Result<(), String> {
    let mut offset = 0;

    while offset < payload.len() {
        if offset + 1 > payload.len() {
            break; // End of payload
        }

        // Read field byte
        let field_byte = payload[offset];
        offset += 1;

        let (type_bits, field_num) = TypeId::decode_field_byte(field_byte);

        match type_bits {
            0 => {
                // U8
                if offset + 1 > payload.len() {
                    return Err("Truncated u8 field".to_string());
                }
                let value = payload[offset];
                offset += 1;
                set_u8_field(telemetry, field_num, value);
            }
            2 => {
                // U32
                if offset + 4 > payload.len() {
                    return Err("Truncated u32 field".to_string());
                }
                let value = u32::from_le_bytes([
                    payload[offset],
                    payload[offset + 1],
                    payload[offset + 2],
                    payload[offset + 3],
                ]);
                offset += 4;
                set_u32_field(telemetry, field_num, value);
            }
            3 => {
                // U64
                if offset + 8 > payload.len() {
                    return Err("Truncated u64 field".to_string());
                }
                let value = u64::from_le_bytes([
                    payload[offset],
                    payload[offset + 1],
                    payload[offset + 2],
                    payload[offset + 3],
                    payload[offset + 4],
                    payload[offset + 5],
                    payload[offset + 6],
                    payload[offset + 7],
                ]);
                offset += 8;
                set_u64_field(telemetry, field_num, value);
            }
            4 => {
                // F32
                if offset + 4 > payload.len() {
                    return Err("Truncated f32 field".to_string());
                }
                let value = f32::from_le_bytes([
                    payload[offset],
                    payload[offset + 1],
                    payload[offset + 2],
                    payload[offset + 3],
                ]);
                offset += 4;
                set_f32_field(telemetry, field_num, value);
            }
            _ => {
                return Err(format!("Unsupported type: {}", type_bits));
            }
        }
    }

    Ok(())
}

/// Set u8 field value
fn set_u8_field(telemetry: &mut TelemetryData, field_num: u8, value: u8) {
    match field_num {
        0 => telemetry.cpu_usage_percent = Some(value),
        _ => {} // Unknown field, ignore
    }
}

/// Set u32 field value
fn set_u32_field(telemetry: &mut TelemetryData, field_num: u8, value: u32) {
    match field_num {
        2 => telemetry.cpu_frequency = Some(value),
        _ => {} // Unknown field, ignore
    }
}

/// Set u64 field value
fn set_u64_field(telemetry: &mut TelemetryData, field_num: u8, value: u64) {
    match field_num {
        3 => telemetry.memory_total = Some(value),
        4 => telemetry.memory_used = Some(value),
        5 => telemetry.memory_available = Some(value),
        6 => telemetry.swap_total = Some(value),
        7 => telemetry.swap_used = Some(value),
        8 => telemetry.disk_total = Some(value),
        9 => telemetry.disk_used = Some(value),
        10 => telemetry.disk_read_bytes = Some(value),
        11 => telemetry.disk_write_bytes = Some(value),
        12 => telemetry.network_rx_bytes = Some(value),
        13 => telemetry.network_tx_bytes = Some(value),
        14 => telemetry.network_rx_packets = Some(value),
        15 => telemetry.network_tx_packets = Some(value),
        16 => telemetry.uptime_seconds = Some(value),
        _ => {} // Unknown field, ignore
    }
}

/// Set f32 field value
fn set_f32_field(telemetry: &mut TelemetryData, field_num: u8, value: f32) {
    match field_num {
        1 => telemetry.cpu_temperature = Some(value),
        _ => {} // Unknown field, ignore
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::encoder;

    #[test]
    fn test_decode_sample() {
        let data = TelemetryData::sample();
        let encoded = encoder::encode(&data).unwrap();
        
        let decoded = decode(&encoded).unwrap();
        
        assert_eq!(decoded.device_id, data.device_id);
        assert_eq!(decoded.uuid, data.uuid);
        assert_eq!(decoded.timestamp, data.timestamp);
        assert_eq!(decoded.sequence_number, data.sequence_number);
        assert_eq!(decoded.cpu_usage_percent, data.cpu_usage_percent);
        assert_eq!(decoded.memory_used, data.memory_used);
    }

    #[test]
    fn test_decode_with_compression() {
        let mut data = TelemetryData::sample();
        data.compression_type = CompressionType::Lz4;
        
        let encoded = encoder::encode(&data).unwrap();
        let decoded = decode(&encoded).unwrap();
        
        assert_eq!(decoded.compression_type, CompressionType::Lz4);
        assert_eq!(decoded.cpu_usage_percent, data.cpu_usage_percent);
    }

    #[test]
    fn test_decode_flags() {
        let mut data = TelemetryData::sample();
        data.is_delta = true;
        data.is_proxied = true;
        
        let encoded = encoder::encode(&data).unwrap();
        let decoded = decode(&encoded).unwrap();
        
        assert_eq!(decoded.is_delta, true);
        assert_eq!(decoded.is_proxied, true);
    }

    #[test]
    fn test_decode_invalid_checksum() {
        let data = TelemetryData::sample();
        let mut encoded = encoder::encode(&data).unwrap();
        
        // Corrupt checksum
        let len = encoded.len();
        encoded[len - 1] ^= 0xFF;
        
        let result = decode(&encoded);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Checksum mismatch"));
    }

    #[test]
    fn test_decode_truncated() {
        let data = TelemetryData::sample();
        let encoded = encoder::encode(&data).unwrap();
        
        // Truncate packet
        let truncated = &encoded[..10];
        
        let result = decode(truncated);
        assert!(result.is_err());
    }

    #[test]
    fn test_roundtrip() {
        let original = TelemetryData::sample();
        let encoded = encoder::encode(&original).unwrap();
        let decoded = decode(&encoded).unwrap();
        
        // Verify all fields match
        assert_eq!(decoded.device_id, original.device_id);
        assert_eq!(decoded.timestamp, original.timestamp);
        assert_eq!(decoded.cpu_usage_percent, original.cpu_usage_percent);
        assert_eq!(decoded.cpu_temperature, original.cpu_temperature);
        assert_eq!(decoded.memory_total, original.memory_total);
        assert_eq!(decoded.disk_used, original.disk_used);
        assert_eq!(decoded.network_rx_bytes, original.network_rx_bytes);
    }
}
