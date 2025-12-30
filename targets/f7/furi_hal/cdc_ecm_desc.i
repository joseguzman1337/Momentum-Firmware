
#include <furi_hal_usb_i.h>
#include "usb_cdce.h"
#include "usb.h"
#include "usb_cdc.h"
#include "furi_hal_usb_cdc.h"

// Define ECM endpoints if they aren't available
#ifndef CDC1_RXD_EP
#define CDC1_RXD_EP 0x04
#endif
#ifndef CDC1_TXD_EP
#define CDC1_TXD_EP 0x85
#endif
#ifndef CDC1_NTF_EP
#define CDC1_NTF_EP 0x86
#endif

// Define CDC0 endpoints if they aren't available
#ifndef CDC0_RXD_EP
#define CDC0_RXD_EP 0x01
#endif
#ifndef CDC0_TXD_EP
#define CDC0_TXD_EP 0x82
#endif
#ifndef CDC0_NTF_EP
#define CDC0_NTF_EP 0x83
#endif

#ifndef CDC_NTF_SZ
#define CDC_NTF_SZ 8
#endif

/* Device configuration descriptor - Composite ACM + ECM */

struct CdcEcmIadDescriptor {
    struct usb_iad_descriptor comm_iad;
    struct usb_interface_descriptor comm;
    struct usb_cdc_header_desc cdc_hdr;
    struct usb_cdc_call_mgmt_desc cdc_mgmt;
    struct usb_cdc_acm_desc cdc_acm;
    struct usb_cdc_union_desc cdc_union;
    struct usb_endpoint_descriptor comm_ep;
    struct usb_interface_descriptor data;
    struct usb_endpoint_descriptor data_eprx;
    struct usb_endpoint_descriptor data_eptx;

    struct usb_iad_descriptor ecm_iad;
    struct usb_interface_descriptor ecm_comm;
    struct usb_cdc_header_desc ecm_header;
    struct usb_cdc_union_desc ecm_union;
    struct usb_cdc_ether_desc cdc_eth;
    struct usb_endpoint_descriptor ecm_comm_ep;
    struct usb_interface_descriptor ecm_data;
    struct usb_endpoint_descriptor ecm_data_eprx;
    struct usb_endpoint_descriptor ecm_data_eptx;
};

struct CdcEcmConfigDescriptor {
    struct usb_config_descriptor config;
    struct CdcEcmIadDescriptor iad;
} FURI_PACKED;

static const struct CdcEcmConfigDescriptor cdc_ecm_cfg_desc = {
    .config =
        {
            .bLength = sizeof(struct usb_config_descriptor),
            .bDescriptorType = USB_DTYPE_CONFIGURATION,
            .wTotalLength = sizeof(struct CdcEcmConfigDescriptor),
            .bNumInterfaces = 4,

            .bConfigurationValue = 1,
            .iConfiguration = NO_DESCRIPTOR,
            .bmAttributes = USB_CFG_ATTR_RESERVED | USB_CFG_ATTR_SELFPOWERED,
            .bMaxPower = USB_CFG_POWER_MA(500),
        },
    .iad =
        {
            // First Interface Pair: CDC ACM (Serial)
            .comm_iad =
                {
                    .bLength = sizeof(struct usb_iad_descriptor),
                    .bDescriptorType = USB_DTYPE_INTERFASEASSOC,
                    .bFirstInterface = 0,
                    .bInterfaceCount = 2,
                    .bFunctionClass = USB_CLASS_CDC,
                    .bFunctionSubClass = USB_CDC_SUBCLASS_ACM,
                    .bFunctionProtocol = USB_PROTO_NONE,
                    .iFunction = NO_DESCRIPTOR,
                },
            .comm =
                {
                    .bLength = sizeof(struct usb_interface_descriptor),
                    .bDescriptorType = USB_DTYPE_INTERFACE,
                    .bInterfaceNumber = 0,
                    .bAlternateSetting = 0,
                    .bNumEndpoints = 1,
                    .bInterfaceClass = USB_CLASS_CDC,
                    .bInterfaceSubClass = USB_CDC_SUBCLASS_ACM,
                    .bInterfaceProtocol = USB_PROTO_NONE,
                    .iInterface = NO_DESCRIPTOR,
                },
            .cdc_hdr =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_header_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_HEADER,
                    .bcdCDC = VERSION_BCD(1, 1, 0),
                },
            .cdc_mgmt =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_call_mgmt_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_CALL_MANAGEMENT,
                    .bmCapabilities = 0,
                    .bDataInterface = 1,
                },
            .cdc_acm =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_acm_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_ACM,
                    .bmCapabilities = 0,
                },
            .cdc_union =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_union_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_UNION,
                    .bMasterInterface0 = 0,
                    .bSlaveInterface0 = 1,
                },
            .comm_ep =
                {
                    .bLength = sizeof(struct usb_endpoint_descriptor),
                    .bDescriptorType = USB_DTYPE_ENDPOINT,
                    .bEndpointAddress = CDC0_NTF_EP,
                    .bmAttributes = USB_EPTYPE_INTERRUPT,
                    .wMaxPacketSize = CDC_NTF_SZ,
                    .bInterval = 0xFF,
                },
            .data =
                {
                    .bLength = sizeof(struct usb_interface_descriptor),
                    .bDescriptorType = USB_DTYPE_INTERFACE,
                    .bInterfaceNumber = 1,
                    .bAlternateSetting = 0,
                    .bNumEndpoints = 2,
                    .bInterfaceClass = USB_CLASS_CDC_DATA,
                    .bInterfaceSubClass = USB_SUBCLASS_NONE,
                    .bInterfaceProtocol = USB_PROTO_NONE,
                    .iInterface = NO_DESCRIPTOR,
                },
            .data_eprx =
                {
                    .bLength = sizeof(struct usb_endpoint_descriptor),
                    .bDescriptorType = USB_DTYPE_ENDPOINT,
                    .bEndpointAddress = CDC0_RXD_EP,
                    .bmAttributes = USB_EPTYPE_BULK,
                    .wMaxPacketSize = CDC_DATA_SZ,
                    .bInterval = 0x01,
                },
            .data_eptx =
                {
                    .bLength = sizeof(struct usb_endpoint_descriptor),
                    .bDescriptorType = USB_DTYPE_ENDPOINT,
                    .bEndpointAddress = CDC0_TXD_EP,
                    .bmAttributes = USB_EPTYPE_BULK,
                    .wMaxPacketSize = CDC_DATA_SZ,
                    .bInterval = 0x01,
                },

            // Second Interface Pair: CDC ECM (Ethernet)
            .ecm_iad =
                {
                    .bLength = sizeof(struct usb_iad_descriptor),
                    .bDescriptorType = USB_DTYPE_INTERFASEASSOC,
                    .bFirstInterface = 2,
                    .bInterfaceCount = 2,
                    .bFunctionClass = USB_CLASS_CDC,
                    .bFunctionSubClass = USB_CDC_SUBCLASS_ETH,
                    .bFunctionProtocol = USB_PROTO_NONE,
                    .iFunction = NO_DESCRIPTOR,
                },
            .ecm_comm =
                {
                    .bLength = sizeof(struct usb_interface_descriptor),
                    .bDescriptorType = USB_DTYPE_INTERFACE,
                    .bInterfaceNumber = 2,
                    .bAlternateSetting = 0,
                    .bNumEndpoints = 1,
                    .bInterfaceClass = USB_CLASS_CDC,
                    .bInterfaceSubClass = USB_CDC_SUBCLASS_ETH,
                    .bInterfaceProtocol = USB_PROTO_NONE,
                    .iInterface = NO_DESCRIPTOR,
                },
            .ecm_header =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_header_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_HEADER,
                    .bcdCDC = VERSION_BCD(1, 1, 0),
                },
            .ecm_union =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_union_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_UNION,
                    .bMasterInterface0 = 2,
                    .bSlaveInterface0 = 3,
                },
            .cdc_eth =
                {
                    .bFunctionLength = sizeof(struct usb_cdc_ether_desc),
                    .bDescriptorType = USB_DTYPE_CS_INTERFACE,
                    .bDescriptorSubType = USB_DTYPE_CDC_ETHERNET,
                    .iMACAddress = UsbDevMac,
                    .bmEthernetStatistics = 0,
                    .wMaxSegmentSize = 1514,
                    .wNumberMCFilters = 0,
                    .bNumberPowerFilters = 0,
                },
            .ecm_comm_ep =
                {
                    .bLength = sizeof(struct usb_endpoint_descriptor),
                    .bDescriptorType = USB_DTYPE_ENDPOINT,
                    .bEndpointAddress = CDC1_NTF_EP,
                    .bmAttributes = USB_EPTYPE_INTERRUPT,
                    .wMaxPacketSize = CDC_NTF_SZ,
                    .bInterval = 0xFF,
                },
            .ecm_data =
                {
                    .bLength = sizeof(struct usb_interface_descriptor),
                    .bDescriptorType = USB_DTYPE_INTERFACE,
                    .bInterfaceNumber = 3,
                    .bAlternateSetting = 0,
                    .bNumEndpoints = 2,
                    .bInterfaceClass = USB_CLASS_CDC_DATA,
                    .bInterfaceSubClass = USB_SUBCLASS_NONE,
                    .bInterfaceProtocol = USB_PROTO_NONE,
                    .iInterface = NO_DESCRIPTOR,
                },
            .ecm_data_eprx =
                {
                    .bLength = sizeof(struct usb_endpoint_descriptor),
                    .bDescriptorType = USB_DTYPE_ENDPOINT,
                    .bEndpointAddress = CDC1_RXD_EP,
                    .bmAttributes = USB_EPTYPE_BULK,
                    .wMaxPacketSize = CDC_DATA_SZ,
                    .bInterval = 0x01,
                },
            .ecm_data_eptx =
                {
                    .bLength = sizeof(struct usb_endpoint_descriptor),
                    .bDescriptorType = USB_DTYPE_ENDPOINT,
                    .bEndpointAddress = CDC1_TXD_EP,
                    .bmAttributes = USB_EPTYPE_BULK,
                    .wMaxPacketSize = CDC_DATA_SZ,
                    .bInterval = 0x01,
                },
        },
};
