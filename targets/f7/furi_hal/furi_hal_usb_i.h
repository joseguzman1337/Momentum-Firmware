#pragma once

#include "usb.h"

#define USB_EP0_SIZE 8

/* String descriptors */
enum {
    UsbDevLang = 0x00,
    UsbDevManuf,
    UsbDevProduct,
    UsbDevSerial,
    UsbDevMac,
};
