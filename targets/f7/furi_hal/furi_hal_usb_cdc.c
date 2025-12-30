#include <furi_hal_version.h>
#include <furi_hal_usb_i.h>
#include <furi_hal_usb.h>
#include <furi_hal_usb_cdc.h>
#include <furi.h>

#include "usb.h"
#include "usb_cdc.h"
#include "usb_cdce.h"

#define CDC0_RXD_EP 0x01
#define CDC0_TXD_EP 0x82
#define CDC0_NTF_EP 0x83

#define CDC1_RXD_EP 0x04
#define CDC1_TXD_EP 0x85
#define CDC1_NTF_EP 0x86

#define CDC_NTF_SZ 0x08

#define IF_NUM_MAX 2

struct CdcIadDescriptor {
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
};

struct CdcConfigDescriptorSingle {
    struct usb_config_descriptor config;
    struct CdcIadDescriptor iad_0;
} FURI_PACKED;

struct CdcConfigDescriptorDual {
    struct usb_config_descriptor config;
    struct CdcIadDescriptor iad_0;
    struct CdcIadDescriptor iad_1;
} FURI_PACKED;

static const struct usb_string_descriptor dev_manuf_desc = USB_STRING_DESC("Flipper Devices Inc.");

/* Device descriptor */
static const struct usb_device_descriptor cdc_device_desc = {
    .bLength = sizeof(struct usb_device_descriptor),
    .bDescriptorType = USB_DTYPE_DEVICE,
    .bcdUSB = VERSION_BCD(2, 0, 0),
    .bDeviceClass = USB_CLASS_IAD,
    .bDeviceSubClass = USB_SUBCLASS_IAD,
    .bDeviceProtocol = USB_PROTO_IAD,
    .bMaxPacketSize0 = USB_EP0_SIZE,
    .idVendor = 0x0483,
    .idProduct = 0x5740,
    .bcdDevice = VERSION_BCD(1, 0, 0),
    .iManufacturer = UsbDevManuf,
    .iProduct = UsbDevProduct,
    .iSerialNumber = UsbDevSerial,
    .bNumConfigurations = 1,
};

/* Device configuration descriptor - single mode*/
static const struct CdcConfigDescriptorSingle cdc_cfg_desc_single = {
    .config =
        {
            .bLength = sizeof(struct usb_config_descriptor),
            .bDescriptorType = USB_DTYPE_CONFIGURATION,
            .wTotalLength = sizeof(struct CdcConfigDescriptorSingle),
            .bNumInterfaces = 2,

            .bConfigurationValue = 1,
            .iConfiguration = NO_DESCRIPTOR,
            .bmAttributes = USB_CFG_ATTR_RESERVED | USB_CFG_ATTR_SELFPOWERED,
            .bMaxPower = USB_CFG_POWER_MA(500),
        },
    .iad_0 =
        {
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
        },
};

#include "cdc_ecm_desc.i"

/* Device descriptor */
static const struct usb_device_descriptor cdc_ecm_device_desc = {
    .bLength = sizeof(struct usb_device_descriptor),
    .bDescriptorType = USB_DTYPE_DEVICE,
    .bcdUSB = VERSION_BCD(2, 0, 0),
    .bDeviceClass = USB_CLASS_IAD,
    .bDeviceSubClass = USB_SUBCLASS_IAD,
    .bDeviceProtocol = USB_PROTO_IAD,
    .bMaxPacketSize0 = USB_EP0_SIZE,
    .idVendor = 0x0483, // STMicroelectronics
    .idProduct = 0x5740, // STM32 Virtual COM Port
    .bcdDevice = VERSION_BCD(1, 0, 0),
    .iManufacturer = 1,
    .iProduct = 2,
    .iSerialNumber = 3,
    .bNumConfigurations = 1,
};

/* Device configuration descriptor - dual mode*/
static const struct CdcConfigDescriptorDual
    cdc_cfg_desc_dual =
        {
            .config =
                {
                    .bLength = sizeof(struct usb_config_descriptor),
                    .bDescriptorType = USB_DTYPE_CONFIGURATION,
                    .wTotalLength = sizeof(struct CdcConfigDescriptorDual),
                    .bNumInterfaces = 4,

                    .bConfigurationValue = 1,
                    .iConfiguration = NO_DESCRIPTOR,
                    .bmAttributes = USB_CFG_ATTR_RESERVED | USB_CFG_ATTR_SELFPOWERED,
                    .bMaxPower = USB_CFG_POWER_MA(500),
                },
            .iad_0 =
                {
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
                },
            .iad_1 =
                {
                    .comm_iad =
                        {
                            .bLength = sizeof(struct usb_iad_descriptor),
                            .bDescriptorType = USB_DTYPE_INTERFASEASSOC,
                            .bFirstInterface = 2,
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
                            .bInterfaceNumber = 2 + 0,
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
                            .bDataInterface = 2 + 1,
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
                            .bMasterInterface0 = 2 + 0,
                            .bSlaveInterface0 = 2 + 1,
                        },
                    .comm_ep =
                        {
                            .bLength = sizeof(struct usb_endpoint_descriptor),
                            .bDescriptorType = USB_DTYPE_ENDPOINT,
                            .bEndpointAddress = CDC1_NTF_EP,
                            .bmAttributes = USB_EPTYPE_INTERRUPT,
                            .wMaxPacketSize = CDC_NTF_SZ,
                            .bInterval = 0xFF,
                        },
                    .data =
                        {
                            .bLength = sizeof(struct usb_interface_descriptor),
                            .bDescriptorType = USB_DTYPE_INTERFACE,
                            .bInterfaceNumber = 2 + 1,
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
                            .bEndpointAddress = CDC1_RXD_EP,
                            .bmAttributes = USB_EPTYPE_BULK,
                            .wMaxPacketSize = CDC_DATA_SZ,
                            .bInterval = 0x01,
                        },
                    .data_eptx =
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

static struct usb_cdc_line_coding cdc_config[IF_NUM_MAX] = {};
static uint8_t cdc_ctrl_line_state[IF_NUM_MAX];

static void cdc_init(usbd_device* dev, FuriHalUsbInterface* intf, void* ctx);
static void cdc_deinit(usbd_device* dev);
static void cdc_on_wakeup(usbd_device* dev);
static void cdc_on_suspend(usbd_device* dev);

static usbd_respond cdc_ep_config(usbd_device* dev, uint8_t cfg);
static usbd_respond cdc_control(usbd_device* dev, usbd_ctlreq* req, usbd_rqc_callback* callback);

static usbd_device* usb_dev;
static volatile FuriHalUsbInterface* cdc_if_cur = NULL;
static volatile bool connected = false;
static volatile CdcCallbacks* callbacks[IF_NUM_MAX] = {NULL};
static void* cb_ctx[IF_NUM_MAX];

FuriHalUsbInterface usb_cdc_single = {
    .init = cdc_init,
    .deinit = cdc_deinit,
    .wakeup = cdc_on_wakeup,
    .suspend = cdc_on_suspend,

    .dev_descr = (struct usb_device_descriptor*)&cdc_device_desc,

    .str_manuf_descr = (void*)&dev_manuf_desc,
    .str_prod_descr = NULL,
    .str_serial_descr = NULL,

    .cfg_descr = (void*)&cdc_cfg_desc_single,
};

FuriHalUsbInterface usb_cdc_dual = {
    .init = cdc_init,
    .deinit = cdc_deinit,
    .wakeup = cdc_on_wakeup,
    .suspend = cdc_on_suspend,

    .dev_descr = (struct usb_device_descriptor*)&cdc_device_desc,

    .str_manuf_descr = (void*)&dev_manuf_desc,
    .str_prod_descr = NULL,
    .str_serial_descr = NULL,

    .cfg_descr = (void*)&cdc_cfg_desc_dual,
};

static void cdc_init_ecm(usbd_device* dev, FuriHalUsbInterface* intf, void* ctx);

FuriHalUsbInterface usb_cdc_ecm = {
    .init = cdc_init_ecm, // We use a wrapper to init both
    .deinit = cdc_deinit,
    .wakeup = cdc_on_wakeup,
    .suspend = cdc_on_suspend,

    .dev_descr = (struct usb_device_descriptor*)&cdc_ecm_device_desc,

    .str_manuf_descr = (void*)&dev_manuf_desc,
    .str_prod_descr = NULL,
    .str_serial_descr = NULL,

    .cfg_descr = (void*)&cdc_ecm_cfg_desc,
};

static void cdc_init(usbd_device* dev, FuriHalUsbInterface* intf, void* ctx) {
    UNUSED(ctx);
    usb_dev = dev;
    cdc_if_cur = intf;

    char* name = (char*)furi_hal_version_get_device_name_ptr();
    uint8_t len = (name == NULL) ? (0) : (strlen(name));
    struct usb_string_descriptor* dev_prod_desc = malloc(len * 2 + 2);
    dev_prod_desc->bLength = len * 2 + 2;
    dev_prod_desc->bDescriptorType = USB_DTYPE_STRING;
    for(uint8_t i = 0; i < len; i++) {
        dev_prod_desc->wString[i] = name[i];
    }

    name = (char*)furi_hal_version_get_name_ptr();
    len = (name == NULL) ? (0) : (strlen(name));
    struct usb_string_descriptor* dev_serial_desc = malloc((len + 5) * 2 + 2);
    dev_serial_desc->bLength = (len + 5) * 2 + 2;
    dev_serial_desc->bDescriptorType = USB_DTYPE_STRING;
    memcpy(dev_serial_desc->wString, "f\0l\0i\0p\0_\0", 5 * 2);
    for(uint8_t i = 0; i < len; i++) {
        dev_serial_desc->wString[i + 5] = name[i];
    }

    cdc_if_cur->str_prod_descr = dev_prod_desc;
    cdc_if_cur->str_serial_descr = dev_serial_desc;

    usbd_reg_config(dev, cdc_ep_config);
    usbd_reg_control(dev, cdc_control);

    usbd_connect(dev, true);
}

// Special Init for ECM Composite
static uint8_t mac_addr_bytes[6] = {0x02, 0x00, 0x00, 0x00, 0x00, 0x00};
static struct usb_string_descriptor* mac_addr_desc = NULL;
static void cdc_init_ecm(usbd_device* dev, FuriHalUsbInterface* intf, void* ctx) {
    // Standard CDC init
    cdc_init(dev, intf, ctx);

    // Additional MAC generation
    const char* name = (char*)furi_hal_version_get_device_name_ptr();
    uint8_t len = (name == NULL) ? (0) : (strlen(name));

    // MAC Address
    if(mac_addr_desc) free(mac_addr_desc);
    struct usb_string_descriptor* mac = malloc(12 * 2 + 2);
    mac->bLength = 12 * 2 + 2;
    mac->bDescriptorType = USB_DTYPE_STRING;

    mac_addr_bytes[0] = 0x02; // Locally Administered
    for(int i = 1; i < 6; i++)
        mac_addr_bytes[i] = 0x00;

    for(int i = 0; i < len; i++) {
        mac_addr_bytes[(i % 5) + 1] ^= name[i];
    }

    for(int i = 0; i < 6; i++) {
        uint8_t hi = (mac_addr_bytes[i] >> 4) & 0x0F;
        uint8_t lo = mac_addr_bytes[i] & 0x0F;
        mac->wString[i * 2] = (hi < 10) ? ('0' + hi) : ('A' + hi - 10);
        mac->wString[i * 2 + 1] = (lo < 10) ? ('0' + lo) : ('A' + lo - 10);
    }
    mac_addr_desc = mac;
    cdc_if_cur->str_mac_descr = mac_addr_desc;
}

static void cdc_deinit(usbd_device* dev) {
    usbd_reg_config(dev, NULL);
    usbd_reg_control(dev, NULL);

    free(cdc_if_cur->str_prod_descr);
    free(cdc_if_cur->str_serial_descr);

    cdc_if_cur = NULL;
    if(mac_addr_desc) {
        free(mac_addr_desc);
        mac_addr_desc = NULL;
    }
}

void furi_hal_cdc_set_callbacks(uint8_t if_num, CdcCallbacks* cb, void* context) {
    furi_check(if_num < IF_NUM_MAX);

    if(callbacks[if_num] != NULL) {
        if(callbacks[if_num]->state_callback != NULL) {
            if(connected == true) callbacks[if_num]->state_callback(cb_ctx[if_num], 0);
        }
    }

    callbacks[if_num] = cb;
    cb_ctx[if_num] = context;

    if(callbacks[if_num] != NULL) {
        if(callbacks[if_num]->state_callback != NULL) {
            if(connected == true) callbacks[if_num]->state_callback(cb_ctx[if_num], 1);
        }
        if(callbacks[if_num]->ctrl_line_callback != NULL) {
            callbacks[if_num]->ctrl_line_callback(cb_ctx[if_num], cdc_ctrl_line_state[if_num]);
        }
    }
}

struct usb_cdc_line_coding* furi_hal_cdc_get_port_settings(uint8_t if_num) {
    furi_check(if_num < IF_NUM_MAX);
    return &cdc_config[if_num];
}

uint8_t furi_hal_cdc_get_ctrl_line_state(uint8_t if_num) {
    furi_check(if_num < IF_NUM_MAX);
    return cdc_ctrl_line_state[if_num];
}

void furi_hal_cdc_send(uint8_t if_num, uint8_t* buf, uint16_t len) {
    if(if_num == 0) {
        usbd_ep_write(usb_dev, CDC0_TXD_EP, buf, len);
    } else if(if_num == 1) {
        usbd_ep_write(usb_dev, CDC1_TXD_EP, buf, len);
    } else {
        furi_crash();
    }
}

int32_t furi_hal_cdc_receive(uint8_t if_num, uint8_t* buf, uint16_t max_len) {
    int32_t len = 0;
    if(if_num == 0) {
        len = usbd_ep_read(usb_dev, CDC0_RXD_EP, buf, max_len);
    } else if(if_num == 1) {
        len = usbd_ep_read(usb_dev, CDC1_RXD_EP, buf, max_len);
    } else {
        furi_crash();
    }
    return (len < 0) ? 0 : len;
}

static void cdc_on_wakeup(usbd_device* dev) {
    UNUSED(dev);
    connected = true;
    for(uint8_t i = 0; i < IF_NUM_MAX; i++) {
        if(callbacks[i] != NULL) {
            if(callbacks[i]->state_callback != NULL) callbacks[i]->state_callback(cb_ctx[i], 1);
        }
    }
}

static void cdc_on_suspend(usbd_device* dev) {
    UNUSED(dev);
    connected = false;
    for(uint8_t i = 0; i < IF_NUM_MAX; i++) {
        cdc_ctrl_line_state[i] = 0;
        if(callbacks[i] != NULL) {
            if(callbacks[i]->state_callback != NULL) callbacks[i]->state_callback(cb_ctx[i], 0);
        }
    }
}

static void cdc_rx_ep_callback(usbd_device* dev, uint8_t event, uint8_t ep) {
    UNUSED(dev);
    UNUSED(event);
    uint8_t if_num = 0;
    if(ep == CDC0_RXD_EP) {
        if_num = 0;
    } else {
        if_num = 1;
    }

    if(callbacks[if_num] != NULL) {
        if(callbacks[if_num]->rx_ep_callback != NULL) {
            callbacks[if_num]->rx_ep_callback(cb_ctx[if_num]);
        }
    }
}

// ECM RX Handler
static FuriHalUsbNetworkReceiveCallback net_rx_callback = NULL;
static void* net_rx_context = NULL;
static uint8_t net_rx_buf[CDC_DATA_SZ];

static void ecm_rx_ep_callback(usbd_device* dev, uint8_t event, uint8_t ep) {
    UNUSED(event);
    UNUSED(ep);
    if(net_rx_callback) {
        int32_t len = usbd_ep_read(dev, CDC1_RXD_EP, net_rx_buf, CDC_DATA_SZ);
        if(len > 0) {
            net_rx_callback(net_rx_buf, (uint16_t)len, net_rx_context);
        }
    }
}

static void cdc_tx_ep_callback(usbd_device* dev, uint8_t event, uint8_t ep) {
    UNUSED(dev);
    UNUSED(event);
    uint8_t if_num = 0;
    if(ep == CDC0_TXD_EP) {
        if_num = 0;
    } else {
        if_num = 1;
    }

    if(callbacks[if_num] != NULL) {
        if(callbacks[if_num]->tx_ep_callback != NULL) {
            callbacks[if_num]->tx_ep_callback(cb_ctx[if_num]);
        }
    }
}

static void cdc_txrx_ep_callback(usbd_device* dev, uint8_t event, uint8_t ep) {
    if(event == usbd_evt_eptx) {
        cdc_tx_ep_callback(dev, event, ep);
    } else {
        cdc_rx_ep_callback(dev, event, ep);
    }
}

/* Configure endpoints */
static usbd_respond cdc_ep_config(usbd_device* dev, uint8_t cfg) {
    uint8_t if_cnt = ((struct usb_config_descriptor*)(cdc_if_cur->cfg_descr))->bNumInterfaces;
    switch(cfg) {
    case 0:
        /* deconfiguring device */
        // ECM Deconfig
        if(cdc_if_cur == &usb_cdc_ecm) {
            usbd_ep_deconfig(dev, CDC1_NTF_EP);
            usbd_ep_deconfig(dev, CDC1_TXD_EP);
            usbd_ep_deconfig(dev, CDC1_RXD_EP);
            usbd_reg_endpoint(dev, CDC1_RXD_EP, 0);
            usbd_reg_endpoint(dev, CDC1_TXD_EP, 0);
        } else if(if_cnt == 4) {
            usbd_ep_deconfig(dev, CDC1_NTF_EP);
            usbd_ep_deconfig(dev, CDC1_TXD_EP);
            usbd_ep_deconfig(dev, CDC1_RXD_EP);
            usbd_reg_endpoint(dev, CDC1_RXD_EP, 0);
            usbd_reg_endpoint(dev, CDC1_TXD_EP, 0);
        }
        usbd_ep_deconfig(dev, CDC0_NTF_EP);
        usbd_ep_deconfig(dev, CDC0_TXD_EP);
        usbd_ep_deconfig(dev, CDC0_RXD_EP);
        usbd_reg_endpoint(dev, CDC0_RXD_EP, 0);
        usbd_reg_endpoint(dev, CDC0_TXD_EP, 0);
        return usbd_ack;
    case 1:
        /* configuring device */
        if((CDC0_TXD_EP & 0x7F) != (CDC0_RXD_EP & 0x7F)) {
            // 2x unidirectional endpoint mode with dualbuf
            usbd_ep_config(dev, CDC0_RXD_EP, USB_EPTYPE_BULK | USB_EPTYPE_DBLBUF, CDC_DATA_SZ);
            usbd_ep_config(dev, CDC0_TXD_EP, USB_EPTYPE_BULK | USB_EPTYPE_DBLBUF, CDC_DATA_SZ);
            usbd_ep_config(dev, CDC0_NTF_EP, USB_EPTYPE_INTERRUPT, CDC_NTF_SZ);
            usbd_reg_endpoint(dev, CDC0_RXD_EP, cdc_rx_ep_callback);
            usbd_reg_endpoint(dev, CDC0_TXD_EP, cdc_tx_ep_callback);
        } else {
            // 1x bidirectional endpoint mode
            usbd_ep_config(dev, CDC0_RXD_EP, USB_EPTYPE_BULK, CDC_DATA_SZ);
            usbd_ep_config(dev, CDC0_TXD_EP, USB_EPTYPE_BULK, CDC_DATA_SZ);
            usbd_ep_config(dev, CDC0_NTF_EP, USB_EPTYPE_INTERRUPT, CDC_NTF_SZ);
            usbd_reg_endpoint(dev, CDC0_RXD_EP, cdc_txrx_ep_callback);
            usbd_reg_endpoint(dev, CDC0_TXD_EP, cdc_txrx_ep_callback);
        }
        usbd_ep_write(dev, CDC0_TXD_EP, 0, 0);

        // ECM Config
        if(cdc_if_cur == &usb_cdc_ecm) {
            usbd_ep_config(dev, CDC1_RXD_EP, USB_EPTYPE_BULK, CDC_DATA_SZ);
            usbd_ep_config(dev, CDC1_TXD_EP, USB_EPTYPE_BULK, CDC_DATA_SZ);
            usbd_ep_config(dev, CDC1_NTF_EP, USB_EPTYPE_INTERRUPT, CDC_NTF_SZ);
            usbd_reg_endpoint(dev, CDC1_RXD_EP, ecm_rx_ep_callback);
            usbd_ep_write(dev, CDC1_TXD_EP, 0, 0);
            return usbd_ack;
        }

        if(if_cnt == 4) {
            if((CDC1_TXD_EP & 0x7F) != (CDC1_RXD_EP & 0x7F)) {
                usbd_ep_config(dev, CDC1_RXD_EP, USB_EPTYPE_BULK | USB_EPTYPE_DBLBUF, CDC_DATA_SZ);
                usbd_ep_config(dev, CDC1_TXD_EP, USB_EPTYPE_BULK | USB_EPTYPE_DBLBUF, CDC_DATA_SZ);
                usbd_ep_config(dev, CDC1_NTF_EP, USB_EPTYPE_INTERRUPT, CDC_NTF_SZ);
                usbd_reg_endpoint(dev, CDC1_RXD_EP, cdc_rx_ep_callback);
                usbd_reg_endpoint(dev, CDC1_TXD_EP, cdc_tx_ep_callback);
            } else {
                usbd_ep_config(dev, CDC1_RXD_EP, USB_EPTYPE_BULK, CDC_DATA_SZ);
                usbd_ep_config(dev, CDC1_TXD_EP, USB_EPTYPE_BULK, CDC_DATA_SZ);
                usbd_ep_config(dev, CDC1_NTF_EP, USB_EPTYPE_INTERRUPT, CDC_NTF_SZ);
                usbd_reg_endpoint(dev, CDC1_RXD_EP, cdc_txrx_ep_callback);
                usbd_reg_endpoint(dev, CDC1_TXD_EP, cdc_txrx_ep_callback);
            }
            usbd_ep_write(dev, CDC1_TXD_EP, 0, 0);
        }
        return usbd_ack;
    default:
        return usbd_fail;
    }
}

/* Control requests handler */
static usbd_respond cdc_control(usbd_device* dev, usbd_ctlreq* req, usbd_rqc_callback* callback) {
    UNUSED(callback);
    /* CDC control requests */
    uint8_t if_num = 0;
    if(((USB_REQ_RECIPIENT | USB_REQ_TYPE) & req->bmRequestType) ==
           (USB_REQ_INTERFACE | USB_REQ_CLASS) &&
       (req->wIndex == 0 || req->wIndex == 2)) {
        if(req->wIndex == 0) {
            if_num = 0;
        } else {
            if_num = 1;
        }

        // ECM uses Interface 2/3 but Control is on 2.
        // For furi_hal_cdc context, if_num 1 maps to Dual CDC 1.
        // ECM is separate.

        // ECM Specific Request Handling
        if((cdc_if_cur == &usb_cdc_ecm) && (req->wIndex == 2)) {
            switch(req->bRequest) {
            case USB_CDC_SET_ETH_PACKET_FILTER:
                return usbd_ack;
            default:
                return usbd_fail;
            }
        }

        switch(req->bRequest) {
        case USB_CDC_SET_CONTROL_LINE_STATE:
            if(callbacks[if_num] != NULL) {
                cdc_ctrl_line_state[if_num] = req->wValue;
                if(callbacks[if_num]->ctrl_line_callback != NULL) {
                    callbacks[if_num]->ctrl_line_callback(
                        cb_ctx[if_num], cdc_ctrl_line_state[if_num]);
                }
            }
            return usbd_ack;
        case USB_CDC_SET_LINE_CODING:
            memcpy(&cdc_config[if_num], req->data, sizeof(cdc_config[0]));
            if(callbacks[if_num] != NULL) {
                if(callbacks[if_num]->config_callback != NULL) {
                    callbacks[if_num]->config_callback(cb_ctx[if_num], &cdc_config[if_num]);
                }
            }
            return usbd_ack;
        case USB_CDC_GET_LINE_CODING:
            dev->status.data_ptr = &cdc_config[if_num];
            dev->status.data_count = sizeof(cdc_config[0]);
            return usbd_ack;
        default:
            return usbd_fail;
        }
    }
    return usbd_fail;
}

// Ethernet Extension Impl
void furi_hal_usb_ethernet_set_received_callback(
    FuriHalUsbNetworkReceiveCallback callback,
    void* context) {
    net_rx_callback = callback;
    net_rx_context = context;
}
void furi_hal_usb_ethernet_send(uint8_t* buffer, uint16_t len) {
    if(usb_dev) {
        usbd_ep_write(usb_dev, CDC1_TXD_EP, buffer, len);
    }
}
void furi_hal_usb_ethernet_get_mac(uint8_t* mac) {
    memcpy(mac, mac_addr_bytes, 6);
}
void furi_hal_usb_ethernet_set_network_down(void) {
}
void furi_hal_usb_ethernet_set_network_up(void) {
}
