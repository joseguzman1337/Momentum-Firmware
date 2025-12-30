import Foundation
import DriverKit

/// Manages firmware loading and distribution for the RTL8814AU device
class FirmwareLoader {
    
    // MARK: - Properties
    
    private(set) var firmwareData: Data?
    private var firmwareVersion: String?
    
    // MARK: - Constants
    
    private enum Constants {
        static let firmwareExtension = "bin"
        static let expectedMinSize = 1024 // Minimum firmware size in bytes
        static let expectedMaxSize = 1024 * 1024 // Maximum firmware size (1MB)
    }
    
    // MARK: - Initialization
    
    init() {
        os_log("FirmwareLoader initialized", type: .debug)
    }
    
    // MARK: - Public Methods
    
    /// Load firmware from bundle
    /// - Parameter name: Firmware file name (without extension)
    func loadFirmware(named name: String) async throws {
        os_log("Loading firmware: %{public}@", type: .info, name)
        
        // Construct firmware path
        guard let firmwarePath = Bundle.main.path(
            forResource: name,
            ofType: Constants.firmwareExtension
        ) else {
            os_log("Firmware file not found: %{public}@", type: .error, name)
            throw FirmwareError.fileNotFound(name)
        }
        
        // Load firmware data
        let data = try Data(contentsOf: URL(fileURLWithPath: firmwarePath))
        
        // Validate firmware
        try validateFirmware(data)
        
        // Store firmware
        self.firmwareData = data
        
        // Extract version if available
        self.firmwareVersion = extractVersion(from: data)
        
        os_log("Firmware loaded successfully: %{public}@ bytes, version: %{public}@",
               type: .info,
               String(data.count),
               firmwareVersion ?? "unknown")
    }
    
    /// Get firmware data in chunks for transmission
    /// - Parameter chunkSize: Size of each chunk
    /// - Returns: Array of data chunks
    func getFirmwareChunks(chunkSize: Int) -> [Data] {
        guard let firmware = firmwareData else {
            return []
        }
        
        var chunks: [Data] = []
        var offset = 0
        
        while offset < firmware.count {
            let end = min(offset + chunkSize, firmware.count)
            let chunk = firmware[offset..<end]
            chunks.append(chunk)
            offset = end
        }
        
        return chunks
    }
    
    // MARK: - Private Methods
    
    private func validateFirmware(_ data: Data) throws {
        // Check size
        guard data.count >= Constants.expectedMinSize else {
            throw FirmwareError.invalidSize("Firmware too small")
        }
        
        guard data.count <= Constants.expectedMaxSize else {
            throw FirmwareError.invalidSize("Firmware too large")
        }
        
        // Verify firmware header (RTL8814AU specific)
        // First 4 bytes should be a valid magic number
        guard data.count >= 4 else {
            throw FirmwareError.invalidFormat("Missing header")
        }
        
        let header = data.prefix(4)
        let magicNumbers: [[UInt8]] = [
            [0x92, 0x81, 0x00, 0x00], // Common RTL firmware magic
            [0x52, 0x54, 0x4C, 0x38], // "RTL8" ASCII
        ]
        
        let headerBytes = [UInt8](header)
        let isValid = magicNumbers.contains { magic in
            zip(magic, headerBytes).allSatisfy { $0 == $1 }
        }
        
        guard isValid else {
            os_log("Warning: Firmware header doesn't match expected format", type: .default)
            // Don't fail - some firmware variants may have different headers
        }
        
        // Calculate and log checksum
        let checksum = calculateChecksum(data)
        os_log("Firmware checksum: 0x%08x", type: .debug, checksum)
    }
    
    private func calculateChecksum(_ data: Data) -> UInt32 {
        var checksum: UInt32 = 0
        
        for byte in data {
            checksum = checksum &+ UInt32(byte)
        }
        
        return checksum
    }
    
    private func extractVersion(from data: Data) -> String? {
        // Try to extract version string from firmware
        // RTL firmware often contains version info at specific offsets
        
        // Check common version offset (0x18-0x20)
        guard data.count > 0x20 else {
            return nil
        }
        
        let versionData = data[0x18..<0x20]
        
        // Try to interpret as ASCII string
        if let versionString = String(data: versionData, encoding: .ascii) {
            let cleaned = versionString.trimmingCharacters(in: .controlCharacters)
            if !cleaned.isEmpty {
                return cleaned
            }
        }
        
        // Fallback: return hex representation of first few bytes
        let versionBytes = [UInt8](data.prefix(8))
        return versionBytes.map { String(format: "%02x", $0) }.joined()
    }
}

// MARK: - Error Types

enum FirmwareError: Error, LocalizedError {
    case fileNotFound(String)
    case invalidSize(String)
    case invalidFormat(String)
    case checksumMismatch
    
    var errorDescription: String? {
        switch self {
        case .fileNotFound(let name):
            return "Firmware file not found: \(name)"
        case .invalidSize(let reason):
            return "Invalid firmware size: \(reason)"
        case .invalidFormat(let reason):
            return "Invalid firmware format: \(reason)"
        case .checksumMismatch:
            return "Firmware checksum mismatch"
        }
    }
}
