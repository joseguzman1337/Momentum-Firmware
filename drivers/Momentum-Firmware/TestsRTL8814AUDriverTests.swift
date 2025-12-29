import Testing
import Testing
import Foundation
@testable import RTL8814AUDriver

@Suite("RTL8814AU Constants Tests")
struct ConstantsTests {
    
    @Test("Vendor ID is correct")
    func testVendorID() {
        #expect(RTL8814AUConstants.vendorID == 0x0bda)
    }
    
    @Test("Product IDs are valid")
    func testProductIDs() {
        #expect(RTL8814AUConstants.supportedProductIDs.contains(0x8813))
        #expect(RTL8814AUConstants.supportedProductIDs.contains(0x8814))
        #expect(RTL8814AUConstants.supportedProductIDs.count == 2)
    }
    
    @Test("Channel frequency calculation for 2.4 GHz")
    func testChannelFrequency2_4GHz() {
        // Channel 1 should be 2412 MHz
        let freq1 = RTL8814AUConstants.frequency(channel: 1, band: .band2_4GHz)
        #expect(freq1 == 2412)
        
        // Channel 6 should be 2437 MHz
        let freq6 = RTL8814AUConstants.frequency(channel: 6, band: .band2_4GHz)
        #expect(freq6 == 2437)
        
        // Channel 11 should be 2462 MHz
        let freq11 = RTL8814AUConstants.frequency(channel: 11, band: .band2_4GHz)
        #expect(freq11 == 2462)
    }
    
    @Test("Channel frequency calculation for 5 GHz")
    func testChannelFrequency5GHz() {
        // Channel 36 should be 5180 MHz
        let freq36 = RTL8814AUConstants.frequency(channel: 36, band: .band5GHz)
        #expect(freq36 == 5180)
        
        // Channel 149 should be 5745 MHz
        let freq149 = RTL8814AUConstants.frequency(channel: 149, band: .band5GHz)
        #expect(freq149 == 5745)
    }
    
    @Test("Supported device detection")
    func testIsSupportedDevice() {
        #expect(RTL8814AUConstants.isSupported(productID: 0x8813))
        #expect(RTL8814AUConstants.isSupported(productID: 0x8814))
        #expect(!RTL8814AUConstants.isSupported(productID: 0x0000))
        #expect(!RTL8814AUConstants.isSupported(productID: 0xFFFF))
    }
    
    @Test("MIMO configuration")
    func testMIMOConfiguration() {
        #expect(RTL8814AUConstants.Capabilities.txChains == 4)
        #expect(RTL8814AUConstants.Capabilities.rxChains == 4)
    }
    
    @Test("Maximum data rates")
    func testMaxDataRates() {
        #expect(RTL8814AUConstants.Capabilities.maxRate2_4GHz == 800)
        #expect(RTL8814AUConstants.Capabilities.maxRate5GHz == 1733)
    }
    
    @Test("Supported 802.11 standards")
    func testSupportedStandards() {
        #expect(RTL8814AUConstants.Capabilities.supportsA)
        #expect(RTL8814AUConstants.Capabilities.supportsB)
        #expect(RTL8814AUConstants.Capabilities.supportsG)
        #expect(RTL8814AUConstants.Capabilities.supportsN)
        #expect(RTL8814AUConstants.Capabilities.supportsAC)
    }
    
    @Test("Channel lists")
    func testChannelLists() {
        // 2.4 GHz should have 11 channels (US)
        #expect(RTL8814AUConstants.Channels.channels2_4GHz.count == 11)
        #expect(RTL8814AUConstants.Channels.channels2_4GHz.first == 1)
        #expect(RTL8814AUConstants.Channels.channels2_4GHz.last == 11)
        
        // 5 GHz should have multiple channels
        #expect(RTL8814AUConstants.Channels.channels5GHz.count > 0)
        #expect(RTL8814AUConstants.Channels.channels5GHz.contains(36))
        #expect(RTL8814AUConstants.Channels.channels5GHz.contains(149))
    }
}

@Suite("RTL8814AU Driver Tests")
struct DriverTests {
    
    @Test("Driver initialization")
    func testDriverInitialization() async throws {
        // This would require mocking IOUSBHostDevice
        // For now, just verify the class exists
        #expect(RTL8814AUDriver.self != nil)
    }
}

@Suite("USB Interface Tests")
struct USBInterfaceTests {
    
    @Test("Register address calculations")
    func testRegisterAddresses() {
        #expect(RTL8814AUConstants.Register.macAddr == 0x0010)
        #expect(RTL8814AUConstants.Register.rxConfig == 0x0608)
        #expect(RTL8814AUConstants.Register.txConfig == 0x0610)
    }
    
    @Test("Endpoint addresses")
    func testEndpointAddresses() {
        #expect(RTL8814AUConstants.Endpoint.bulkIn == 0x81)
        #expect(RTL8814AUConstants.Endpoint.bulkOut1 == 0x01)
        #expect(RTL8814AUConstants.Endpoint.interruptIn == 0x84)
    }
}

@Suite("WiFi Interface Tests")
struct WiFiInterfaceTests {
    
    @Test("Power level validation")
    func testPowerLevelValidation() {
        let defaultPower = RTL8814AUConstants.Power.defaultTxPower
        let maxPower = RTL8814AUConstants.Power.maxTxPower
        let minPower = RTL8814AUConstants.Power.minTxPower
        
        #expect(defaultPower >= minPower)
        #expect(defaultPower <= maxPower)
        #expect(minPower < maxPower)
    }
    
    @Test("Buffer sizes")
    func testBufferSizes() {
        #expect(RTL8814AUConstants.BufferSize.maxUSBPacket == 512)
        #expect(RTL8814AUConstants.BufferSize.maxFrame == 2346)
        #expect(RTL8814AUConstants.BufferSize.txBuffer > 0)
        #expect(RTL8814AUConstants.BufferSize.rxBuffer > 0)
    }
}

@Suite("Firmware Tests")
struct FirmwareTests {
    
    @Test("Firmware parameters")
    func testFirmwareParameters() {
        #expect(RTL8814AUConstants.Firmware.chunkSize == 4096)
        #expect(RTL8814AUConstants.Firmware.maxSize == 32768)
        #expect(RTL8814AUConstants.Firmware.chunkSize < RTL8814AUConstants.Firmware.maxSize)
    }
}
