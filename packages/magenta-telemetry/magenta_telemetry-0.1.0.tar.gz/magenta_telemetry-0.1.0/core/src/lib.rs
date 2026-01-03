//! Magenta Telemetry Format - Core Library
//!
//! Ultra-lightweight binary serialization format for telemetry data.
//!
//! # Example
//!
//! ```
//! use magenta_telemetry_core::{TelemetryData, encode, decode, CompressionType};
//!
//! // Create telemetry data
//! let mut data = TelemetryData::sample();
//! data.compression_type = CompressionType::Lz4;
//!
//! // Encode to binary
//! let bytes = encode(&data).expect("Encoding failed");
//!
//! // Decode from binary
//! let decoded = decode(&bytes).expect("Decoding failed");
//!
//! assert_eq!(decoded.device_id, data.device_id);
//! ```

pub mod types;
pub mod encoder;
pub mod decoder;
pub mod compression;
pub mod delta;

// Re-export main types and functions
pub use types::{CompressionType, TelemetryData, FieldId, TypeId};
pub use encoder::encode;
pub use decoder::decode;
pub use delta::{compute_delta, apply_delta};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_full_roundtrip() {
        let data = TelemetryData::sample();
        let bytes = encode(&data).unwrap();
        let decoded = decode(&bytes).unwrap();
        
        assert_eq!(decoded.device_id, data.device_id);
        assert_eq!(decoded.timestamp, data.timestamp);
    }

    #[test]
    fn test_compression_roundtrip() {
        let mut data = TelemetryData::sample();
        data.compression_type = CompressionType::Lz4;
        
        let bytes = encode(&data).unwrap();
        let decoded = decode(&bytes).unwrap();
        
        assert_eq!(decoded.compression_type, CompressionType::Lz4);
        assert_eq!(decoded.cpu_usage_percent, data.cpu_usage_percent);
    }

    #[test]
    fn test_delta_workflow() {
        let snapshot1 = TelemetryData::sample();
        let mut snapshot2 = snapshot1.clone();
        snapshot2.cpu_usage_percent = Some(95);
        snapshot2.sequence_number += 1;

        // Compute delta
        let delta = compute_delta(&snapshot1, &snapshot2);
        assert!(delta.is_delta);

        // Encode delta
        let delta_bytes = encode(&delta).unwrap();
        
        // Should be smaller than full encoding
        let full_bytes = encode(&snapshot2).unwrap();
        assert!(delta_bytes.len() < full_bytes.len());

        // Decode delta
        let decoded_delta = decode(&delta_bytes).unwrap();
        
        // Apply delta
        let reconstructed = apply_delta(&snapshot1, &decoded_delta);
        assert_eq!(reconstructed.cpu_usage_percent, Some(95));
    }
}
