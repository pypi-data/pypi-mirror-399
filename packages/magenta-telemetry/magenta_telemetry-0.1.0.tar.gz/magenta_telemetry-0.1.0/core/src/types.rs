//! Magenta Telemetry Format - Core Data Types
//!
//! This module defines the core data structures for telemetry collection.

/// Compression algorithm types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CompressionType {
    /// No compression
    None = 0,
    /// LZ4 block compression
    Lz4 = 1,
}

impl CompressionType {
    /// Convert from u8 bits (bits 7-5 of flags byte)
    pub fn from_bits(bits: u8) -> Result<Self, String> {
        match bits {
            0 => Ok(CompressionType::None),
            1 => Ok(CompressionType::Lz4),
            _ => Err(format!("Unknown compression type: {}", bits)),
        }
    }

    /// Convert to u8 bits for flags byte
    pub fn to_bits(self) -> u8 {
        self as u8
    }
}

/// Telemetry data structure
#[derive(Debug, Clone)]
pub struct TelemetryData {
    // Identity
    pub device_id: String,
    pub uuid: [u8; 16],
    pub timestamp: i64,  // Unix timestamp in milliseconds
    pub sequence_number: u32,
    
    // CPU Metrics
    pub cpu_usage_percent: Option<u8>,       // 0-100
    pub cpu_temperature: Option<f32>,        // Celsius
    pub cpu_frequency: Option<u32>,          // MHz
    
    // Memory Metrics
    pub memory_total: Option<u64>,           // bytes
    pub memory_used: Option<u64>,            // bytes
    pub memory_available: Option<u64>,       // bytes
    pub swap_total: Option<u64>,             // bytes
    pub swap_used: Option<u64>,              // bytes
    
    // Disk Metrics
    pub disk_total: Option<u64>,             // bytes
    pub disk_used: Option<u64>,              // bytes
    pub disk_read_bytes: Option<u64>,        // cumulative
    pub disk_write_bytes: Option<u64>,       // cumulative
    
    // Network Metrics
    pub network_rx_bytes: Option<u64>,       // cumulative
    pub network_tx_bytes: Option<u64>,       // cumulative
    pub network_rx_packets: Option<u64>,     // cumulative
    pub network_tx_packets: Option<u64>,     // cumulative
    
    // System
    pub uptime_seconds: Option<u64>,
    
    // Flags
    pub is_proxied: bool,
    pub is_delta: bool,
    pub compression_type: CompressionType,
}

impl TelemetryData {
    /// Create a new telemetry data instance with required fields
    pub fn new(device_id: String, uuid: [u8; 16], timestamp: i64, sequence_number: u32) -> Self {
        Self {
            device_id,
            uuid,
            timestamp,
            sequence_number,
            cpu_usage_percent: None,
            cpu_temperature: None,
            cpu_frequency: None,
            memory_total: None,
            memory_used: None,
            memory_available: None,
            swap_total: None,
            swap_used: None,
            disk_total: None,
            disk_used: None,
            disk_read_bytes: None,
            disk_write_bytes: None,
            network_rx_bytes: None,
            network_tx_bytes: None,
            network_rx_packets: None,
            network_tx_packets: None,
            uptime_seconds: None,
            is_proxied: false,
            is_delta: false,
            compression_type: CompressionType::None,
        }
    }

    /// Create default instance with sample data (for testing)
    pub fn sample() -> Self {
        let mut uuid = [0u8; 16];
        uuid.copy_from_slice(&[
            0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6, 0x07, 0x18,
            0x29, 0x3A, 0x4B, 0x5C, 0x6D, 0x7E, 0x8F, 0x90,
        ]);

        let mut data = Self::new(
            "magenta-001".to_string(),
            uuid,
            1735686690000,
            42,
        );

        data.cpu_usage_percent = Some(45);
        data.cpu_temperature = Some(65.5);
        data.cpu_frequency = Some(2400);
        data.memory_total = Some(17179869184); // 16GB
        data.memory_used = Some(8589934592);   // 8GB
        data.memory_available = Some(8589934592);
        data.swap_total = Some(4294967296);    // 4GB
        data.swap_used = Some(1073741824);     // 1GB
        data.disk_total = Some(1099511627776); // 1TB
        data.disk_used = Some(549755813888);   // 500GB
        data.disk_read_bytes = Some(12345678901);
        data.disk_write_bytes = Some(98765432109);
        data.network_rx_bytes = Some(1234567890);
        data.network_tx_bytes = Some(987654321);
        data.network_rx_packets = Some(123456);
        data.network_tx_packets = Some(98765);
        data.uptime_seconds = Some(864000); // 10 days

        data
    }

    /// Builder pattern: set CPU usage
    pub fn with_cpu_usage(mut self, percent: u8) -> Self {
        self.cpu_usage_percent = Some(percent.min(100));
        self
    }

    /// Builder pattern: set CPU temperature
    pub fn with_cpu_temp(mut self, temp: f32) -> Self {
        self.cpu_temperature = Some(temp);
        self
    }

    /// Builder pattern: set memory usage
    pub fn with_memory(mut self, total: u64, used: u64, available: u64) -> Self {
        self.memory_total = Some(total);
        self.memory_used = Some(used);
        self.memory_available = Some(available);
        self
    }

    /// Builder pattern: enable compression
    pub fn with_compression(mut self, compression: CompressionType) -> Self {
        self.compression_type = compression;
        self
    }

    /// Builder pattern: mark as proxied
    pub fn with_proxied(mut self, proxied: bool) -> Self {
        self.is_proxied = proxied;
        self
    }

    /// Builder pattern: mark as delta
    pub fn with_delta(mut self, delta: bool) -> Self {
        self.is_delta = delta;
        self
    }
}

/// Field identifiers for payload encoding
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum FieldId {
    CpuUsage = 0,
    CpuTemp = 1,
    CpuFreq = 2,
    MemTotal = 3,
    MemUsed = 4,
    MemAvailable = 5,
    SwapTotal = 6,
    SwapUsed = 7,
    DiskTotal = 8,
    DiskUsed = 9,
    DiskReadBytes = 10,
    DiskWriteBytes = 11,
    NetRxBytes = 12,
    NetTxBytes = 13,
    NetRxPackets = 14,
    NetTxPackets = 15,
    UptimeSeconds = 16,
}

/// Type identifiers for field encoding
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum TypeId {
    U8 = 0,
    U16 = 1,
    U32 = 2,
    U64 = 3,
    F32 = 4,
    F64 = 5,
    Bool = 6,
    Extended = 7,
}

impl TypeId {
    /// Encode field ID byte from type and field number
    pub fn encode_field_byte(self, field_num: u8) -> u8 {
        debug_assert!(field_num < 32, "Field number must be < 32");
        ((self as u8) << 5) | (field_num & 0x1F)
    }

    /// Decode field ID byte into type and field number
    pub fn decode_field_byte(byte: u8) -> (u8, u8) {
        let type_bits = byte >> 5;
        let field_num = byte & 0x1F;
        (type_bits, field_num)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compression_type_conversion() {
        assert_eq!(CompressionType::from_bits(0).unwrap(), CompressionType::None);
        assert_eq!(CompressionType::from_bits(1).unwrap(), CompressionType::Lz4);
        assert!(CompressionType::from_bits(2).is_err());
    }

    #[test]
    fn test_field_id_encoding() {
        let byte = TypeId::U8.encode_field_byte(5);
        assert_eq!(byte, 0b00000101); // Type 0, field 5

        let byte = TypeId::F32.encode_field_byte(12);
        assert_eq!(byte, 0b10001100); // Type 4, field 12

        let (type_bits, field_num) = TypeId::decode_field_byte(0b10001100);
        assert_eq!(type_bits, 4);
        assert_eq!(field_num, 12);
    }

    #[test]
    fn test_telemetry_builder() {
        let uuid = [0u8; 16];
        let data = TelemetryData::new("test".to_string(), uuid, 1234567890, 1)
            .with_cpu_usage(75)
            .with_cpu_temp(55.5)
            .with_compression(CompressionType::Lz4)
            .with_proxied(true);

        assert_eq!(data.cpu_usage_percent, Some(75));
        assert_eq!(data.cpu_temperature, Some(55.5));
        assert_eq!(data.compression_type, CompressionType::Lz4);
        assert_eq!(data.is_proxied, true);
    }

    #[test]
    fn test_sample_data() {
        let sample = TelemetryData::sample();
        assert_eq!(sample.device_id, "magenta-001");
        assert_eq!(sample.sequence_number, 42);
        assert!(sample.cpu_usage_percent.is_some());
        assert!(sample.memory_used.is_some());
    }
}
