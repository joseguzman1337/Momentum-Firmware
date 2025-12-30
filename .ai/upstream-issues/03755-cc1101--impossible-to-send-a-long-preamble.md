# Issue #3755: CC1101: Impossible to send a long preamble

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3755](https://github.com/flipperdevices/flipperzero-firmware/issues/3755)
**Author:** @krzys-h
**Created:** 2024-07-05T07:36:23Z
**Labels:** Sub-GHz, Bug

## Description

### Describe the enhancement you're suggesting.

Hi! I'm currently trying to replicate a [custom base station for old electronic price tags](https://github.com/atc1441/E-Paper_Pricetags/tree/main/Custom_PriceTag_AccesPoint) using a Flipper. Since these tags use the CC1110 chip (the variant of CC1101 integrated with a 8051 MCU), they should be a perfect match for the CC1101 in the Flipper. However, since the communication protocol is quite a bit more complicated than what the Flipper usually deals with, I'm running into some limitations of the software API interface exposed to the applications.

The price tags I'm working with use a very peculiar battery saving measure. When not in use, they shut down completely, including the radio. Every 15 seconds or so, they wake up, check the wakeup channels for presence of a carrier (there are two, one for the EU and one for the US), and if nothing is transmitting, immediately go back to sleep. To wake them up, you need to start transmitting on the frequency, sleep for 15 seconds or so to ensure the tag has woken up, and only then send the actual packet.

According to some other implementation I'm referencing and the CC1101 datasheet, the way to achieve this is to first switch the chip to TX mode, which will immediately start transmitting the preamble on the frequency, and send the packet after some time when we actually want to start transmitting.

<details>
<summary>Quote from the CC1101 datasheet</summary>

> The preamble pattern is an alternating
> sequence of ones and zeros (10101010…).
> The minimum length of the preamble is
> programmable through the value of
> MDMCFG1.NUM_PREAMBLE. When enabling
> TX, the modulator will start transmitting the
> preamble. When the programmed number of
> preamble bytes has been transmitted, the
> modulator will send the sync word and then
> data from the TX FIFO if data is available. If
> the TX FIFO is empty, the modulator will
> continue to send preamble bytes until the first
> byte is written to the TX FIFO. The modulator
> will then send the sync word and then the data
> bytes. 
</details>

On the Flipper, you would expect this to translate to something along the lines of:
```c
subghz_devices_set_tx(device);
for(int i = 15; i > 0; i--) {
    FURI_LOG_I(TAG, "%d", i);
    furi_delay_ms(1000);
}
uint8_t wakeup_packet[10] = { ... data ... };
subghz_devices_write_packet(device, wakeup_packet, 10);
```

This, however, does not work, and the radio chip stops transmitting the preamble and enters the `IDLE` state when `subghz_devices_write_packet` is called. This is because this function internally causes the `SFTX` strobe to be sent, which is technically undefined behavior, as the datasheet specifies that it can only be called while in `IDLE` or `TX_UNDERFLOW` states.

```c
void furi_hal_subghz_write_packet(const uint8_t* data, uint8_t size) {
    furi_check(data);
    furi_check(size);

    furi_hal_spi_acquire(&furi_hal_spi_bus_handle_subghz);
    cc1101_flush_tx(&furi_hal_spi_bus_handle_subghz);     // <---- problem here
    cc1101_write_reg(&furi_hal_spi_bus_handle_subghz, CC1101_FIFO, size);
    cc1101_write_fifo(&furi_hal_spi_bus_handle_subghz, data, size);
    furi_hal_spi_release(&furi_hal_spi_bus_handle_subghz);
}
```

I'm not sure what the best way to fix this without breaking backwards compatibility of the interface would be, but I definitely wouldn't expect the `write_packet` function to switch radio modes.

As far as I can tell, the firmware doesn't expose any more direct `cc1101_*` routines to the applications, so to workaround this you need to copy a few of the functions into the app and control the SPI bus pretty much directly (ouch).

### Anything else?

`read_packet` does not have this problem, and flushing the FIFO is left up to the application.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
