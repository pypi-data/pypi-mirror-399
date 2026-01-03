//! Magenta Telemetry Format - Compression Module
//!
//! Handles LZ4 compression and decompression.

/// Compress data using LZ4
pub fn compress_lz4(data: &[u8]) -> Result<Vec<u8>, String> {
    Ok(lz4_flex::compress_prepend_size(data))
}

/// Decompress LZ4 data
pub fn decompress_lz4(data: &[u8]) -> Result<Vec<u8>, String> {
    lz4_flex::decompress_size_prepended(data)
        .map_err(|e| format!("LZ4 decompression failed: {}", e))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lz4_roundtrip() {
        let original = b"Hello, Magenta! This is a test of LZ4 compression. ".repeat(10);
        
        let compressed = compress_lz4(&original).unwrap();
        assert!(compressed.len() < original.len(), "Compression should reduce size");
        
        let decompressed = decompress_lz4(&compressed).unwrap();
        assert_eq!(decompressed, original);
    }

    #[test]
    fn test_lz4_small_data() {
        let original = b"Hi";
        
        let compressed = compress_lz4(original).unwrap();
        let decompressed = decompress_lz4(&compressed).unwrap();
        
        assert_eq!(decompressed, original);
    }

    #[test]
    fn test_lz4_empty() {
        let original = b"";
        
        let compressed = compress_lz4(original).unwrap();
        let decompressed = decompress_lz4(&compressed).unwrap();
        
        assert_eq!(decompressed, original);
    }

    #[test]
    fn test_lz4_invalid() {
        let invalid = b"this is not valid lz4 data";
        let result = decompress_lz4(invalid);
        assert!(result.is_err());
    }
}
