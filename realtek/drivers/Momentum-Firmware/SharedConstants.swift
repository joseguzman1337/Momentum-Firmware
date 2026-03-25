import Foundation

/// Hardware constants for RTL8814AU chipset
enum RTL8814AUConstants {
    
    // MARK: - USB Identifiers
    
    /// Realtek Vendor ID
    static let vendorID: UInt16 = 0x0bda
    
    /// Supported Product IDs for RTL8814AU
    static let supportedProductIDs: [UInt16] = [
        0x8813, // RTL8814AU
        0x8814  // RTL8814AU variant
    ]
    
    // MARK: - USB Endpoints
    
    enum Endpoint {
        /// Bulk IN endpoint for receiving data
        static let bulkIn: UInt8 = 0x81
        
        /// Bulk OUT endpoints for transmitting data
        static let bulkOut1: UInt8 = 0x01
        static let bulkOut2: UInt8 = 0x02
        static let bulkOut3: UInt8 = 0x03
        
        /// Interrupt IN endpoint for events
        static let interruptIn: UInt8 = 0x84
    }
    
    // MARK: - Register Addresses
    
    enum Register {
        // System registers
        static let sysFunc: UInt16 = 0x0002
        static let sysClock: UInt16 = 0x0007
        static let sysReset: UInt16 = 0x0005
        
        // MAC address registers
        static let macAddr: UInt16 = 0x0010
        
        // Command registers
        static let cr: UInt16 = 0x0100
        
        // Interrupt registers
        static let imr: UInt16 = 0x0120
        static let isr: UInt16 = 0x0130
        
        // RX/TX registers
        static let rxConfig: UInt16 = 0x0608
        static let txConfig: UInt16 = 0x0610
        
        // RF registers
        static let rfConfig: UInt16 = 0x0900
        static let rfPath0: UInt16 = 0x0800
        static let rfPath1: UInt16 = 0x0880
        static let rfPath2: UInt16 = 0x0C80
        static let rfPath3: UInt16 = 0x0E00
    }
    
    // MARK: - Firmware
    
    enum Firmware {
        /// Firmware version expected
        static let version = "40.0"
        
        /// Firmware chunk size for upload
        static let chunkSize = 4096
        
        /// Maximum firmware size
        static let maxSize = 32768 // 32KB
    }
    
    // MARK: - WiFi Capabilities
    
    enum Capabilities {
        // PHY capabilities
        static let supports2_4GHz = true
        static let supports5GHz = true
        
        // 802.11 standards
        static let supportsA = true
        static let supportsB = true
        static let supportsG = true
        static let supportsN = true
        static let supportsAC = true
        
        // MIMO configuration
        static let txChains = 4
        static let rxChains = 4
        
        // Maximum data rates
        static let maxRate2_4GHz = 800  // Mbps
        static let maxRate5GHz = 1733   // Mbps
        
        // Channel widths
        static let supports20MHz = true
        static let supports40MHz = true
        static let supports80MHz = true
        
        // Other capabilities
        static let supportsBeamforming = true
        static let supportsShortGI = true
        static let supportsLDPC = true
        static let supportsSTBC = true
    }
    
    // MARK: - Channels
    
    enum Channels {
        /// 2.4 GHz channels (North America)
        static let channels2_4GHz: [UInt8] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        
        /// 5 GHz channels (North America)
        static let channels5GHz: [UInt8] = [
            36, 40, 44, 48,           // UNII-1
            52, 56, 60, 64,           // UNII-2A
            100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, // UNII-2C
            149, 153, 157, 161, 165   // UNII-3
        ]
    }
    
    // MARK: - Power
    
    enum Power {
        /// Default transmit power (dBm)
        static let defaultTxPower = 20
        
        /// Maximum transmit power (dBm)
        static let maxTxPower = 30
        
        /// Minimum transmit power (dBm)
        static let minTxPower = 1
    }
    
    // MARK: - Timeouts
    
    enum Timeout {
        /// USB control transfer timeout (milliseconds)
        static let controlTransfer: UInt32 = 500
        
        /// USB bulk transfer timeout (milliseconds)
        static let bulkTransfer: UInt32 = 1000
        
        /// Firmware load timeout (seconds)
        static let firmwareLoad: UInt32 = 10
        
        /// Scan timeout per channel (milliseconds)
        static let scanPerChannel: UInt32 = 100
        
        /// Connection timeout (seconds)
        static let connection: UInt32 = 30
    }
    
    // MARK: - Buffer Sizes
    
    enum BufferSize {
        /// Maximum USB packet size
        static let maxUSBPacket = 512
        
        /// Maximum 802.11 frame size
        static let maxFrame = 2346
        
        /// TX buffer size
        static let txBuffer = 4096
        
        /// RX buffer size
        static let rxBuffer = 8192
    }
    
    // MARK: - Driver Info
    
    enum DriverInfo {
        static let name = "RTL8814AU"
        static let version = "1.0.0"
        static let author = "Open Source Community"
        static let description = "Realtek RTL8814AU USB WiFi Driver for macOS"
    }
}

// MARK: - Helper Extensions

extension RTL8814AUConstants {
    /// Check if a product ID is supported
    static func isSupported(productID: UInt16) -> Bool {
        return supportedProductIDs.contains(productID)
    }
    
    /// Get frequency for a channel
    static func frequency(channel: UInt8, band: Band) -> UInt32 {
        switch band {
        case .band2_4GHz:
            return 2407 + (UInt32(channel) * 5)
        case .band5GHz:
            return 5000 + (UInt32(channel) * 5)
        }
    }
    
    enum Band {
        case band2_4GHz
        case band5GHz
    }
}
