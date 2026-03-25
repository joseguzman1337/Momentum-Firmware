/*
 * RTL88xxAU USB WiFi Driver for macOS
 * Based on Linux RTL8812AU/RTL8821AU/RTL8814AU driver
 * 
 * Copyright (c) 2024 Realtek
 */

#ifndef RTL88XXAU_H
#define RTL88XXAU_H

#include <libkern/c++/OSObject.h>
#include <libkern/c++/OSDictionary.h>
#include <IOKit/IOService.h>
#include <IOKit/usb/IOUSBInterface.h>
#include <IOKit/usb/IOUSBDevice.h>
#include <IOKit/usb/IOUSBPipe.h>
#include <IOKit/network/IOEthernetController.h>
#include <IOKit/network/IOEthernetInterface.h>
#include <IOKit/network/IOGatedOutputQueue.h>
#include <IOKit/IOBufferMemoryDescriptor.h>
#include <IOKit/IOWorkLoop.h>
#include <IOKit/IOCommandGate.h>
#include <IOKit/IOLog.h>

// Vendor and Product IDs
#define REALTEK_VENDOR_ID   0x0BDA

// RTL8812AU Product IDs
#define RTL8812AU_PID_1     0x8812
#define RTL8812AU_PID_2     0x881A
#define RTL8812AU_PID_3     0x8822

// RTL8821AU Product IDs  
#define RTL8821AU_PID_1     0x8821
#define RTL8821AU_PID_2     0x0821
#define RTL8821AU_PID_3     0x0823

// RTL8814AU Product IDs
#define RTL8814AU_PID_1     0x8813
#define RTL8814AU_PID_2     0x8814

// Alfa Product IDs
#define ALFA_AWUS1900_PID   0x8021
#define ALFA_AWUS036ACS_PID 0x8022

// USB Configuration
#define USB_CONFIG_VALUE    1
#define USB_INTERFACE_NUM   0

// Buffer sizes
#define MAX_RECEIVE_BUFFER  2048
#define MAX_TRANSMIT_BUFFER 2048

// Driver version
#define DRIVER_VERSION "1.0.0"
#define DRIVER_BUILD   "001"

class RTL88xxAU : public IOEthernetController
{
    OSDeclareDefaultStructors(RTL88xxAU)
    
private:
    IOUSBInterface *fInterface;
    IOUSBDevice    *fDevice;
    IOWorkLoop     *fWorkLoop;
    IOCommandGate  *fCommandGate;
    
    // Device information
    UInt16 fVendorID;
    UInt16 fProductID;
    UInt8  fChipType;
    
    // Network interface
    IOEthernetInterface *fNetworkInterface;
    
    // USB pipes
    IOUSBPipe *fInPipe;
    IOUSBPipe *fOutPipe;
    IOUSBPipe *fInterruptPipe;
    
    // Memory descriptors
    IOBufferMemoryDescriptor *fReceiveBuffer;
    IOBufferMemoryDescriptor *fTransmitBuffer;
    
    // Status flags
    bool fStarted;
    bool fEnabled;
    bool fLinkUp;
    
public:
    // IOService overrides
    virtual bool init(OSDictionary *properties = nullptr) override;
    virtual void free() override;
    virtual bool start(IOService *provider) override;
    virtual void stop(IOService *provider) override;
    virtual IOReturn message(UInt32 type, IOService *provider, void *argument) override;
    
    // IO80211Controller overrides
    virtual bool createWorkLoop() override;
    virtual IOWorkLoop *getWorkLoop() const override;
    
    // Network interface methods
    virtual IOReturn enable(IONetworkInterface *netif) override;
    virtual IOReturn disable(IONetworkInterface *netif) override;
    virtual IOReturn outputStart(IONetworkInterface *interface, IOOptionBits options) override;
    
    // USB methods
    virtual IOReturn configureDevice();
    virtual IOReturn openPipes();
    virtual IOReturn closePipes();
    
    // Hardware methods
    virtual IOReturn initHardware();
    virtual IOReturn resetDevice();
    virtual IOReturn powerOn();
    virtual IOReturn powerOff();
    
    // Data transfer methods
    virtual void handleReceiveComplete(void *parameter, IOReturn status, UInt32 bufferSizeRemaining);
    virtual void handleTransmitComplete(void *parameter, IOReturn status, UInt32 bufferSizeRemaining);
    
    // Utility methods
    virtual const char *getDriverName() const;
    virtual const char *getDriverVersion() const;
    virtual UInt32 getChipType() const;
    virtual bool isDeviceSupported(UInt16 vendorID, UInt16 productID);
};

#endif /* RTL88XXAU_H */
