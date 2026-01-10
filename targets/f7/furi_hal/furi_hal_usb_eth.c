#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <furi_hal_version.h>
#include "furi_hal_usb_i.h"
#include <furi_hal_usb.h>
#include <furi_hal_usb_eth.h>
#include <furi.h>
#include <furi/core/log.h>
#include <storage/storage.h>

#include <usb.h>
#include <usb_std.h>
#include <usb_cdc.h>

#include <lwip/init.h>
#include <lwip/netif.h>
#include <lwip/etharp.h>
#include <lwip/dhcp.h>
#include <lwip/tcpip.h>
#include <netif/ethernet.h>
#include <lwip/apps/http_client.h>

#include <furi/core/semaphore.h>

#define TAG "FuriHalUsbEth"

/* CDC-ECM Class Codes */
#define USB_CDC_SUBCLASS_ECM 0x06
#define USB_DTYPE_CDC_ECM    0x0F

/* CDC-ECM Ethernet Networking Functional Descriptor */
struct usb_cdc_ecm_desc {
    uint8_t bLength;
    uint8_t bDescriptorType;
    uint8_t bDescriptorSubType;
    uint8_t iMACAddress;
    uint32_t bmEthernetStatistics;
    uint16_t wMaxSegmentSize;
    uint16_t wNumberMCFilters;
    uint8_t bNumberPowerFilters;
} __attribute__((packed));

#define ETH_RNDIS_RX_EP  0x01
#define ETH_RNDIS_TX_EP  0x82
#define ETH_RNDIS_NTF_EP 0x83

#define ETH_RNDIS_DATA_SZ 64
#define ETH_RNDIS_NTF_SZ  8

struct EthEcmDescriptor {
    struct usb_iad_descriptor iad;
    struct usb_interface_descriptor comm;
    struct usb_cdc_header_desc cdc_hdr;
    struct usb_cdc_union_desc cdc_union;
    struct usb_cdc_ecm_desc ecm_desc;
    struct usb_endpoint_descriptor ntf_ep;
    struct usb_interface_descriptor data;
    struct usb_endpoint_descriptor data_rx;
    struct usb_endpoint_descriptor data_tx;
} __attribute__((packed));

struct EthConfigDescriptor {
    struct usb_config_descriptor config;
    struct EthEcmDescriptor ecm;
} __attribute__((packed));

static const struct usb_device_descriptor eth_device_desc = {
    .bLength = sizeof(struct usb_device_descriptor),
    .bDescriptorType = USB_DTYPE_DEVICE,
    .bcdUSB = VERSION_BCD(2, 0, 0),
    .bDeviceClass = USB_CLASS_IAD,
    .bDeviceSubClass = 0x02,
    .bDeviceProtocol = 0x01,
    .bMaxPacketSize0 = USB_EP0_SIZE,
    .idVendor = 0x0483,
    .idProduct = 0x5741,
    .bcdDevice = VERSION_BCD(1, 0, 0),
    .iManufacturer = UsbDevManuf,
    .iProduct = UsbDevProduct,
    .iSerialNumber = UsbDevSerial,
    .bNumConfigurations = 1,
};

static const struct EthConfigDescriptor eth_cfg_desc = {
    .config = {
        .bLength = sizeof(struct usb_config_descriptor),
        .bDescriptorType = USB_DTYPE_CONFIGURATION,
        .wTotalLength = sizeof(struct EthConfigDescriptor),
        .bNumInterfaces = 2,
        .bConfigurationValue = 1,
        .iConfiguration = NO_DESCRIPTOR,
        .bmAttributes = USB_CFG_ATTR_RESERVED | USB_CFG_ATTR_SELFPOWERED,
        .bMaxPower = USB_CFG_POWER_MA(500),
    },
    .ecm = {
        .iad = {
            .bLength = sizeof(struct usb_iad_descriptor),
            .bDescriptorType = USB_DTYPE_INTERFASEASSOC,
            .bFirstInterface = 0,
            .bInterfaceCount = 2,
            .bFunctionClass = USB_CLASS_CDC,
            .bFunctionSubClass = USB_CDC_SUBCLASS_ECM,
            .bFunctionProtocol = 0x00,
            .iFunction = NO_DESCRIPTOR,
        },
        .comm = {
            .bLength = sizeof(struct usb_interface_descriptor),
            .bDescriptorType = USB_DTYPE_INTERFACE,
            .bInterfaceNumber = 0,
            .bAlternateSetting = 0,
            .bNumEndpoints = 1,
            .bInterfaceClass = USB_CLASS_CDC,
            .bInterfaceSubClass = USB_CDC_SUBCLASS_ECM,
            .bInterfaceProtocol = 0x00,
            .iInterface = NO_DESCRIPTOR,
        },
        .cdc_hdr = {
            .bFunctionLength = sizeof(struct usb_cdc_header_desc),
            .bDescriptorType = USB_DTYPE_CS_INTERFACE,
            .bDescriptorSubType = USB_DTYPE_CDC_HEADER,
            .bcdCDC = VERSION_BCD(1, 1, 0),
        },
        .cdc_union = {
            .bFunctionLength = sizeof(struct usb_cdc_union_desc),
            .bDescriptorType = USB_DTYPE_CS_INTERFACE,
            .bDescriptorSubType = USB_DTYPE_CDC_UNION,
            .bMasterInterface0 = 0,
            .bSlaveInterface0 = 1,
        },
        .ecm_desc = {
            .bLength = sizeof(struct usb_cdc_ecm_desc),
            .bDescriptorType = USB_DTYPE_CS_INTERFACE,
            .bDescriptorSubType = USB_DTYPE_CDC_ECM,
            .iMACAddress = UsbDevEthMac,
            .bmEthernetStatistics = 0,
            .wMaxSegmentSize = 1514,
            .wNumberMCFilters = 0,
            .bNumberPowerFilters = 0,
        },
        .ntf_ep = {
            .bLength = sizeof(struct usb_endpoint_descriptor),
            .bDescriptorType = USB_DTYPE_ENDPOINT,
            .bEndpointAddress = ETH_RNDIS_NTF_EP,
            .bmAttributes = USB_EPTYPE_INTERRUPT,
            .wMaxPacketSize = ETH_RNDIS_NTF_SZ,
            .bInterval = 0x01,
        },
        .data = {
            .bLength = sizeof(struct usb_interface_descriptor),
            .bDescriptorType = USB_DTYPE_INTERFACE,
            .bInterfaceNumber = 1,
            .bAlternateSetting = 0,
            .bNumEndpoints = 2,
            .bInterfaceClass = USB_CLASS_CDC_DATA,
            .bInterfaceSubClass = 0x00,
            .bInterfaceProtocol = 0x00,
            .iInterface = NO_DESCRIPTOR,
        },
        .data_rx = {
            .bLength = sizeof(struct usb_endpoint_descriptor),
            .bDescriptorType = USB_DTYPE_ENDPOINT,
            .bEndpointAddress = ETH_RNDIS_RX_EP,
            .bmAttributes = USB_EPTYPE_BULK,
            .wMaxPacketSize = ETH_RNDIS_DATA_SZ,
            .bInterval = 0x01,
        },
        .data_tx = {
            .bLength = sizeof(struct usb_endpoint_descriptor),
            .bDescriptorType = USB_DTYPE_ENDPOINT,
            .bEndpointAddress = ETH_RNDIS_TX_EP,
            .bmAttributes = USB_EPTYPE_BULK,
            .wMaxPacketSize = ETH_RNDIS_DATA_SZ,
            .bInterval = 0x01,
        },
    },
};

static const struct usb_string_descriptor eth_mac_desc = USB_STRING_DESC("F20000000001");

static void eth_init(usbd_device* dev, FuriHalUsbInterface* intf, void* ctx);
static void eth_deinit(usbd_device* dev);
static void eth_on_wakeup(usbd_device* dev);
static void eth_on_suspend(usbd_device* dev);
static usbd_respond eth_ep_config(usbd_device* dev, uint8_t cfg);
static usbd_respond eth_control(usbd_device* dev, usbd_ctlreq* req, usbd_rqc_callback* callback);

FuriHalUsbInterface usb_eth = {
    .init = eth_init,
    .deinit = eth_deinit,
    .wakeup = eth_on_wakeup,
    .suspend = eth_on_suspend,
    .dev_descr = (struct usb_device_descriptor*)&eth_device_desc,
    .str_manuf_descr = NULL,
    .str_prod_descr = NULL,
    .str_serial_descr = NULL,
    .str_eth_mac_descr = (void*)&eth_mac_desc,
    .cfg_descr = (void*)&eth_cfg_desc,
};

static usbd_device* usb_dev;
static bool eth_connected = false;
static struct netif eth_netif;

static err_t eth_low_level_output(struct netif* netif, struct pbuf* p) {
    UNUSED(netif);
    if(!eth_connected) return ERR_CONN;

    static uint8_t tx_buf[2048];
    pbuf_copy_partial(p, tx_buf, p->tot_len, 0);

    if(usbd_ep_write(usb_dev, ETH_RNDIS_TX_EP, tx_buf, p->tot_len) < 0) {
        return ERR_IF;
    }

    return ERR_OK;
}

static err_t eth_netif_init(struct netif* netif) {
    netif->name[0] = 'u';
    netif->name[1] = 'e';
    netif->output = etharp_output;
    netif->linkoutput = eth_low_level_output;
    netif->hwaddr_len = 6;
    
    netif->hwaddr[0] = 0xF2;
    netif->hwaddr[1] = 0x00;
    netif->hwaddr[2] = 0x00;
    netif->hwaddr[3] = 0x00;
    netif->hwaddr[4] = 0x00;
    netif->hwaddr[5] = 0x01;

    netif->mtu = 1500;
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP;

    return ERR_OK;
}

static void eth_rx_callback(usbd_device* dev, uint8_t event, uint8_t ep) {
    UNUSED(dev);
    UNUSED(event);
    UNUSED(ep);

    static uint8_t rx_buf[2048];
    int32_t len = usbd_ep_read(usb_dev, ETH_RNDIS_RX_EP, rx_buf, sizeof(rx_buf));
    if(len > 0) {
        struct pbuf* p = pbuf_alloc(PBUF_RAW, len, PBUF_POOL);
        if(p != NULL) {
            pbuf_take(p, rx_buf, len);
            if(eth_netif.input(p, &eth_netif) != ERR_OK) {
                pbuf_free(p);
            }
        }
    }
}

static void eth_init(usbd_device* dev, FuriHalUsbInterface* intf, void* ctx) {
    UNUSED(intf);
    UNUSED(ctx);
    usb_dev = dev;

    usbd_reg_config(dev, eth_ep_config);
    usbd_reg_control(dev, eth_control);

    static bool lwip_inited = false;
    if(!lwip_inited) {
        tcpip_init(NULL, NULL);
        lwip_inited = true;
    }

    netif_add(&eth_netif, IP4_ADDR_ANY, IP4_ADDR_ANY, IP4_ADDR_ANY, NULL, eth_netif_init, tcpip_input);
    netif_set_default(&eth_netif);
    netif_set_up(&eth_netif);
    dhcp_start(&eth_netif);

    usbd_connect(dev, true);
}

static void eth_deinit(usbd_device* dev) {
    dhcp_stop(&eth_netif);
    netif_set_down(&eth_netif);
    netif_remove(&eth_netif);

    usbd_reg_config(dev, NULL);
    usbd_reg_control(dev, NULL);
}

static void eth_on_wakeup(usbd_device* dev) {
    UNUSED(dev);
    eth_connected = true;
}

static void eth_on_suspend(usbd_device* dev) {
    UNUSED(dev);
    eth_connected = false;
}

static usbd_respond eth_ep_config(usbd_device* dev, uint8_t cfg) {
    switch(cfg) {
    case 0:
        usbd_ep_deconfig(dev, ETH_RNDIS_NTF_EP);
        usbd_ep_deconfig(dev, ETH_RNDIS_TX_EP);
        usbd_ep_deconfig(dev, ETH_RNDIS_RX_EP);
        return usbd_ack;
    case 1:
        usbd_ep_config(dev, ETH_RNDIS_NTF_EP, USB_EPTYPE_INTERRUPT, ETH_RNDIS_NTF_SZ);
        usbd_ep_config(dev, ETH_RNDIS_TX_EP, USB_EPTYPE_BULK, ETH_RNDIS_DATA_SZ);
        usbd_ep_config(dev, ETH_RNDIS_RX_EP, USB_EPTYPE_BULK, ETH_RNDIS_DATA_SZ);
        
        usbd_reg_endpoint(dev, ETH_RNDIS_RX_EP, eth_rx_callback);
        
        return usbd_ack;
    default:
        return usbd_fail;
    }
}

static usbd_respond eth_control(usbd_device* dev, usbd_ctlreq* req, usbd_rqc_callback* callback) {
    UNUSED(dev);
    UNUSED(callback);

    if(((USB_REQ_RECIPIENT | USB_REQ_TYPE) & req->bmRequestType) == (USB_REQ_INTERFACE | USB_REQ_CLASS) && req->wIndex == 0) {
        switch(req->bRequest) {
        case 0x43: /* SET_ETHERNET_PACKET_FILTER */
            return usbd_ack;
        }
    }

    return usbd_fail;
}

/* ---------------- HTTP-over-usb_eth helper implementation ---------------- */

#if LWIP_TCP && LWIP_CALLBACK_API

typedef struct {
    Storage* storage;
    File* file;
    FuriSemaphore* done_sem;

    httpc_connection_t settings;

    httpc_result_t result;
    u32_t rx_content_len;
    u32_t server_response;
    err_t lwip_err;
} UsbEthHttpDownloadContext;

static err_t usb_eth_http_recv(void* arg, struct altcp_pcb* pcb, struct pbuf* p, err_t err) {
    UsbEthHttpDownloadContext* ctx = arg;
    LWIP_UNUSED_ARG(pcb);

    if(err != ERR_OK) {
        if(p != NULL) {
            pbuf_free(p);
        }
        return err;
    }

    if(!p || !ctx || !ctx->file) {
        if(p) pbuf_free(p);
        return ERR_OK;
    }

    struct pbuf* q = p;
    while(q) {
        if(q->len) {
            if(storage_file_write(ctx->file, q->payload, q->len) != q->len) {
                FURI_LOG_E(TAG, "usb_eth_http: storage write failed");
                pbuf_free(p);
                return ERR_MEM;
            }
        }
        q = q->next;
    }

    altcp_recved(pcb, p->tot_len);
    pbuf_free(p);
    return ERR_OK;
}

static void usb_eth_http_result_cb(
    void* arg,
    httpc_result_t httpc_result,
    u32_t rx_content_len,
    u32_t srv_res,
    err_t err) {
    UsbEthHttpDownloadContext* ctx = arg;
    if(!ctx) return;

    ctx->result = httpc_result;
    ctx->rx_content_len = rx_content_len;
    ctx->server_response = srv_res;
    ctx->lwip_err = err;

    /* Signal completion to waiting thread. */
    if(ctx->done_sem) {
        furi_semaphore_release(ctx->done_sem);
    }
}

static bool usb_eth_http_parse_url(
    const char* url,
    char* host,
    size_t host_size,
    u16_t* port,
    const char** out_uri) {
    if(!url || !host || !port || !out_uri) return false;

    const char* prefix = "http://";
    size_t prefix_len = strlen(prefix);
    const char* p = NULL;

    if(strncmp(url, prefix, prefix_len) == 0) {
        p = url + prefix_len;
    } else {
        /* Enforce plain HTTP only; HTTPS is not supported here. */
        FURI_LOG_E(TAG, "usb_eth_http: only http:// URLs are supported");
        return false;
    }

    const char* path = strchr(p, '/');
    if(!path) {
        /* No explicit path -> use root. */
        path = "/";
    }

    const char* host_start = p;
    const char* host_end = path;

    const char* colon = memchr(host_start, ':', (size_t)(host_end - host_start));
    if(colon) {
        host_end = colon;
        long parsed_port = strtol(colon + 1, NULL, 10);
        if(parsed_port <= 0 || parsed_port > 65535) {
            FURI_LOG_E(TAG, "usb_eth_http: invalid port in URL");
            return false;
        }
        *port = (u16_t)parsed_port;
    } else {
        *port = HTTP_DEFAULT_PORT;
    }

    size_t host_len = (size_t)(host_end - host_start);
    if(host_len == 0 || host_len >= host_size) {
        FURI_LOG_E(TAG, "usb_eth_http: host too long or empty");
        return false;
    }

    memcpy(host, host_start, host_len);
    host[host_len] = '\0';

    *out_uri = path;
    return true;
}

bool furi_hal_usb_eth_http_download_to_file(const char* url, const char* dest_path, uint32_t timeout_ms) {
    UNUSED(timeout_ms); /* Currently unused: we wait until HTTP client finishes internally. */

    if(!url || !dest_path) return false;

    if(!eth_connected) {
        FURI_LOG_E(TAG, "usb_eth_http: ethernet link not up");
        return false;
    }

    char host[128];
    u16_t port;
    const char* uri = NULL;

    if(!usb_eth_http_parse_url(url, host, sizeof(host), &port, &uri)) {
        return false;
    }

    Storage* storage = furi_record_open(RECORD_STORAGE);
    if(!storage) {
        FURI_LOG_E(TAG, "usb_eth_http: failed to open storage record");
        return false;
    }

    File* file = storage_file_alloc(storage);
    if(!file) {
        FURI_LOG_E(TAG, "usb_eth_http: failed to alloc file object");
        furi_record_close(RECORD_STORAGE);
        return false;
    }

    if(!storage_file_open(file, dest_path, FSAM_WRITE, FSOM_CREATE_ALWAYS)) {
        FURI_LOG_E(TAG, "usb_eth_http: failed to open dest file %s", dest_path);
        storage_file_free(file);
        furi_record_close(RECORD_STORAGE);
        return false;
    }

    UsbEthHttpDownloadContext ctx = {0};
    ctx.storage = storage;
    ctx.file = file;
    ctx.done_sem = furi_semaphore_alloc(1, 0);
    ctx.settings.use_proxy = 0;
    ctx.settings.result_fn = usb_eth_http_result_cb;
    ctx.settings.headers_done_fn = NULL;

    if(!ctx.done_sem) {
        FURI_LOG_E(TAG, "usb_eth_http: failed to alloc semaphore");
        storage_file_close(file);
        storage_file_free(file);
        furi_record_close(RECORD_STORAGE);
        return false;
    }

    httpc_state_t* connection = NULL;
    err_t err = httpc_get_file_dns(host, port, uri, &ctx.settings, usb_eth_http_recv, &ctx, &connection);
    if(err != ERR_OK) {
        FURI_LOG_E(TAG, "usb_eth_http: httpc_get_file_dns failed (%d)", err);
        furi_semaphore_free(ctx.done_sem);
        storage_file_close(file);
        storage_file_free(file);
        furi_record_close(RECORD_STORAGE);
        return false;
    }

    /* Wait until HTTP client signals completion. Internal HTTP timeouts apply. */
    if(furi_semaphore_acquire(ctx.done_sem, FuriWaitForever) != FuriStatusOk) {
        FURI_LOG_E(TAG, "usb_eth_http: wait for completion failed");
        furi_semaphore_free(ctx.done_sem);
        storage_file_close(file);
        storage_file_free(file);
        furi_record_close(RECORD_STORAGE);
        return false;
    }

    furi_semaphore_free(ctx.done_sem);

    storage_file_sync(file);
    storage_file_close(file);
    storage_file_free(file);
    furi_record_close(RECORD_STORAGE);

    if(ctx.result != HTTPC_RESULT_OK || ctx.lwip_err != ERR_OK) {
        FURI_LOG_E(
            TAG,
            "usb_eth_http: transfer failed (res=%d, lwip=%d, http=%lu)",
            (int)ctx.result,
            (int)ctx.lwip_err,
            (unsigned long)ctx.server_response);
        return false;
    }

    if(ctx.rx_content_len == 0) {
        FURI_LOG_E(TAG, "usb_eth_http: zero-length payload");
        return false;
    }

    return true;
}

#else /* LWIP_TCP && LWIP_CALLBACK_API */

bool furi_hal_usb_eth_http_download_to_file(const char* url, const char* dest_path, uint32_t timeout_ms) {
    UNUSED(url);
    UNUSED(dest_path);
    UNUSED(timeout_ms);

    FURI_LOG_E(TAG, "usb_eth_http: HTTP client not enabled in lwIP config");
    return false;
}

#endif /* LWIP_TCP && LWIP_CALLBACK_API */
