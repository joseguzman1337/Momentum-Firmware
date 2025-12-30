# Issue #3825: C++ Breakpoints not hit

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3825](https://github.com/flipperdevices/flipperzero-firmware/issues/3825)
**Author:** @janwiesemann
**Created:** 2024-08-07T08:46:44Z
**Labels:** Build System & Scripts, Core+Services

## Description

### Describe the bug.

I'm currently trying to develop a small application for FZ. It utilizes some C++ Code and I would like to debug it. Sadly, it does not work. FreeRTOS and hardware close development is relatively new for me. I'm able to add C breakpoints. Yes, I could definitely write it in C but where is the fun in that?

Any help or hint would be appreciated.

### Setup:
- JLink Mini EDU
- VS-Code
- fbt (application in `applications_user/`; not using ufbt)
- firmware repo [release @ 0.104.0](https://github.com/flipperdevices/flipperzero-firmware/releases/tag/0.104.0)

### Reproduction

1. Create a new app
2. Add some C++ code
3. build it and try to attach a debugger to the application

### Target

f7 with VS-Code and C++

### Logs
**VS-Code Debug Console**
```Text
Cortex-Debug: VSCode debugger extension version 1.12.1 git(652d042). Usage info: https://github.com/Marus/cortex-debug#usage
Reading symbols from /Users/user/Projects/flipper/flipperzero-firmware/toolchain/current/bin/arm-none-eabi-objdump --syms -C -h -w /Users/user/Projects/flipper/flipperzero-firmware/build/latest/firmware.elf
Reading symbols from /Users/user/Projects/flipper/flipperzero-firmware/toolchain/current/bin/arm-none-eabi-nm --defined-only -S -l -C -p /Users/user/Projects/flipper/flipperzero-firmware/build/latest/firmware.elf
Launching GDB: /Users/user/Projects/flipper/flipperzero-firmware/toolchain/current/bin/arm-none-eabi-gdb-py3 -q --interpreter=mi2
    IMPORTANT: Set "showDevDebugOutput": "raw" in "launch.json" to see verbose GDB transactions here. Very helpful to debug issues or report problems
Launching gdb-server: JLinkGDBServer -singlerun -nogui -if swd -port 50000 -swoport 50001 -telnetport 50002 -device STM32WB55RG -rtos GDBServer/RTOSPlugin_FreeRTOS.dylib
    Please check TERMINAL tab (gdb-server) for output from JLinkGDBServer
Finished reading symbols from objdump: Time: 42 ms
Output radix now set to decimal 10, hex a, octal 12.
Input radix now set to decimal 10, hex a, octal 12.
Finished reading symbols from nm: Time: 767 ms
vPortSuppressTicksAndSleep (expected_idle_ticks=30) at targets/f7/furi_hal/furi_hal_os.c:172
172	        return;
Program stopped, probably due to a reset and/or halt issued by debugger
Firmware version on attached Flipper:
	Version:     0.104.0
	Built on:    24-07-2024
	Git branch:  release
	Git commit:  ee1b8b9f
	Dirty:       False
	HW Target:   7
	Origin:      Official
	Git origin:  git@github.com:user/flipperzero-firmware.git,https://github.com/flipperdevices/flipperzero-firmware.git
Support for Flipper external apps debug is loaded
Set 'build/latest/.extapps' as debug info lookup path for Flipper external apps
Attaching to Flipper firmware
[New Remote target]
[New Thread 536882256]
[New Thread 537080456]
[New Thread 537081676]
[New Thread 536882912]
[New Thread 537106944]
[New Thread 537072504]
[New Thread 537085728]
[New Thread 537083920]
[New Thread 537085336]
[New Thread 536950776]
[New Thread 536886176]
[New Thread 537073724]
[New Thread 536910936]
[New Thread 536909416]
[New Thread 536884472]
[New Thread 537085532]
[New Thread 537074944]
[New Thread 536890328]
[New Thread 537084116]
[New Thread 537079236]

Thread
3 received signal SIGTRAP, Trace/breakpoint trap.
[Switching to Thread 536882256]
vPortSuppressTicksAndSleep (expected_idle_ticks=86) at targets/f7/furi_hal/furi_hal_os.c:172
172	        return;

Thread
3 received signal SIGTRAP, Trace/breakpoint trap.
vPortSuppressTicksAndSleep (expected_idle_ticks=60) at targets/f7/furi_hal/furi_hal_os.c:172
172	        return;
[New Thread 536919432]

Thread
11 received signal SIGTRAP, Trace/breakpoint trap.
[Switching to Thread 537085336]
loader_start_external_app (error_message=0x2000c250, args=0x0, path=<optimized out>, storage=<optimized out>, loader=0x200066e0) at applications/services/loader/loader.c:530
530	            __asm volatile("bkpt 0");
New application loaded. Adding debug info
Loading debug information from build/latest/.extapps/dolphin_jump_d.elf
add symbol table from file "build/latest/.extapps/dolphin_jump_d.elf" at
	.text_addr = 0x2000c75c
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcj_addr = 0x2000c8f4
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_replaceEjjPKcj_addr = 0x2000d0cc
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3__addr = 0x2000ce1c
	.text._ZNSt15__new_allocatorIcE10deallocateEPcj_addr = 0x2000ab0c
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv_addr = 0x2000ca1c
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7replaceEjjPKcj_addr = 0x2000d25c
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEjjPKcj_addr = 0x2000cf04
	.bss_addr = 0x2000c474
	.rodata_addr = 0x2000d2ac
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_moveEPcPKcj_addr = 0x2000cae4
	.text._ZNSt15__new_allocatorIcE8allocateEjPKv_addr = 0x2000cb44
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERjj_addr = 0x2000cc34
	.text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE12_M_constructIPKcEEvT_S8_St20forward_iterator_tag_addr = 0x2000cc84
warning: section .text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_replaceEjjPKcj not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1IS3_EEPKcRKS3_ not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt15__new_allocatorIcE10deallocateEPcj not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7replaceEjjPKcj not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEjjPKcj not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt15__new_allocatorIcE8allocateEjPKv not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERjj not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
warning: section .text._ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE12_M_constructIPKcEEvT_S8_St20forward_iterator_tag not found in /Users/user/Projects/flipper/flipperzero-firmware/build/f7-firmware-C/.extapps/dolphin_jump_d.elf
Failed to set debug mode: Cannot access memory at address 0x200009cc
```

**Full Build log**
```
rm -rf build/f7-firmware-C/.extapps/ && ./fbt COMPACT=1 DEBUG=0 VERBOSE=1 build APPSRC=applications_user/dolphin-jump/main.cpp

arm-none-eabi-g++ -o build/f7-firmware-C/.extapps/dolphin_jump/Game.o -c -std=c++20 -fno-rtti -fno-use-cxa-atexit -fno-exceptions -fno-threadsafe-statics -ftemplate-depth=4096 -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -mthumb -Wall -Wextra -Werror -Wno-error=deprecated-declarations -Wno-address-of-packed-member -Wredundant-decls -Wdouble-promotion -fdata-sections -ffunction-sections -fsingle-precision-constant -fno-math-errno -g -Os -mword-relocations -mlong-calls -fno-common -nostdlib -D_GNU_SOURCE -DFW_CFG_default -D"M_MEMORY_FULL(x)=abort()" -DSTM32WB -DSTM32WB55xx -DUSE_FULL_ASSERT -DUSE_FULL_LL_DRIVER -DMBEDTLS_CONFIG_FILE=\"mbedtls_cfg.h\" -DPB_ENABLE_MALLOC -DFW_ORIGIN_Official -DFURI_NDEBUG -DNDEBUG -DFAP_VERSION=\"0.1\" -Ifuri -Iapplications/services -Iapplications/main -Itargets/furi_hal_include -Itargets/f7/ble_glue -Itargets/f7/fatfs -Itargets/f7/furi_hal -Itargets/f7/inc -I. -Ilib -Ibuild/f7-firmware-C/assets/compiled -Ilib/mlib -Ilib/cmsis_core -Ilib/stm32wb_cmsis/Include -Ilib/stm32wb_hal/Inc -Ilib/stm32wb_copro/wpan -Ilib/drivers -Ilib/FreeRTOS-Kernel/include -Ilib/FreeRTOS-Kernel/portable/GCC/ARM_CM4F -Ilib/FreeRTOS-glue -Ilib/microtar/src -Ilib/mbedtls/include -Ilib/toolbox -Ilib/libusb_stm32/inc -Ilib/drivers -Ilib/flipper_format -Ilib/one_wire -Ilib/ibutton -Ilib/infrared/encoder_decoder -Ilib/infrared/worker -Ilib/littlefs -Ilib/subghz -Ilib/nfc -Ilib/digital_signal -Ilib/pulse_reader -Ilib/signal_reader -Ilib/app-scened-template -Ilib/callback-connector -Ilib/u8g2 -Ilib/lfrfid -Ilib/flipper_application -Ilib/music_worker -Ilib/mjs -Ilib/nanopb -Ilib/heatshrink -Ilib/ble_profile -Ilib/bit_lib -Ilib/datetime -Ibuild/f7-firmware-C/.extapps/dolphin_jump -Iapplications_user/dolphin-jump applications_user/dolphin-jump/Game.cpp
python3 scripts/assets.py icons applications_user/dolphin-jump/images build/f7-firmware-C/.extapps/dolphin_jump --filename dolphin_jump_icons
arm-none-eabi-g++ -o build/f7-firmware-C/.extapps/dolphin_jump/main.o -c -std=c++20 -fno-rtti -fno-use-cxa-atexit -fno-exceptions -fno-threadsafe-statics -ftemplate-depth=4096 -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -mthumb -Wall -Wextra -Werror -Wno-error=deprecated-declarations -Wno-address-of-packed-member -Wredundant-decls -Wdouble-promotion -fdata-sections -ffunction-sections -fsingle-precision-constant -fno-math-errno -g -Os -mword-relocations -mlong-calls -fno-common -nostdlib -D_GNU_SOURCE -DFW_CFG_default -D"M_MEMORY_FULL(x)=abort()" -DSTM32WB -DSTM32WB55xx -DUSE_FULL_ASSERT -DUSE_FULL_LL_DRIVER -DMBEDTLS_CONFIG_FILE=\"mbedtls_cfg.h\" -DPB_ENABLE_MALLOC -DFW_ORIGIN_Official -DFURI_NDEBUG -DNDEBUG -DFAP_VERSION=\"0.1\" -Ifuri -Iapplications/services -Iapplications/main -Itargets/furi_hal_include -Itargets/f7/ble_glue -Itargets/f7/fatfs -Itargets/f7/furi_hal -Itargets/f7/inc -I. -Ilib -Ibuild/f7-firmware-C/assets/compiled -Ilib/mlib -Ilib/cmsis_core -Ilib/stm32wb_cmsis/Include -Ilib/stm32wb_hal/Inc -Ilib/stm32wb_copro/wpan -Ilib/drivers -Ilib/FreeRTOS-Kernel/include -Ilib/FreeRTOS-Kernel/portable/GCC/ARM_CM4F -Ilib/FreeRTOS-glue -Ilib/microtar/src -Ilib/mbedtls/include -Ilib/toolbox -Ilib/libusb_stm32/inc -Ilib/drivers -Ilib/flipper_format -Ilib/one_wire -Ilib/ibutton -Ilib/infrared/encoder_decoder -Ilib/infrared/worker -Ilib/littlefs -Ilib/subghz -Ilib/nfc -Ilib/digital_signal -Ilib/pulse_reader -Ilib/signal_reader -Ilib/app-scened-template -Ilib/callback-connector -Ilib/u8g2 -Ilib/lfrfid -Ilib/flipper_application -Ilib/music_worker -Ilib/mjs -Ilib/nanopb -Ilib/heatshrink -Ilib/ble_profile -Ilib/bit_lib -Ilib/datetime -Ibuild/f7-firmware-C/.extapps/dolphin_jump -Iapplications_user/dolphin-jump applications_user/dolphin-jump/main.cpp
_validate_api_cache(["targets/f7/api_symbols.csv"], ["build/f7-firmware-C/sdk_origin.i"])
arm-none-eabi-gcc -o build/f7-firmware-C/.extapps/dolphin_jump/dolphin_jump.o -c -std=gnu2x -Wstrict-prototypes -Wno-strict-prototypes -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -mthumb -Wall -Wextra -Werror -Wno-error=deprecated-declarations -Wno-address-of-packed-member -Wredundant-decls -Wdouble-promotion -fdata-sections -ffunction-sections -fsingle-precision-constant -fno-math-errno -g -Os -mword-relocations -mlong-calls -fno-common -nostdlib -D_GNU_SOURCE -DFW_CFG_default -D"M_MEMORY_FULL(x)=abort()" -DSTM32WB -DSTM32WB55xx -DUSE_FULL_ASSERT -DUSE_FULL_LL_DRIVER -DMBEDTLS_CONFIG_FILE=\"mbedtls_cfg.h\" -DPB_ENABLE_MALLOC -DFW_ORIGIN_Official -DFURI_NDEBUG -DNDEBUG -DFAP_VERSION=\"0.1\" -Ifuri -Iapplications/services -Iapplications/main -Itargets/furi_hal_include -Itargets/f7/ble_glue -Itargets/f7/fatfs -Itargets/f7/furi_hal -Itargets/f7/inc -I. -Ilib -Ibuild/f7-firmware-C/assets/compiled -Ilib/mlib -Ilib/cmsis_core -Ilib/stm32wb_cmsis/Include -Ilib/stm32wb_hal/Inc -Ilib/stm32wb_copro/wpan -Ilib/drivers -Ilib/FreeRTOS-Kernel/include -Ilib/FreeRTOS-Kernel/portable/GCC/ARM_CM4F -Ilib/FreeRTOS-glue -Ilib/microtar/src -Ilib/mbedtls/include -Ilib/toolbox -Ilib/libusb_stm32/inc -Ilib/drivers -Ilib/flipper_format -Ilib/one_wire -Ilib/ibutton -Ilib/infrared/encoder_decoder -Ilib/infrared/worker -Ilib/littlefs -Ilib/subghz -Ilib/nfc -Ilib/digital_signal -Ilib/pulse_reader -Ilib/signal_reader -Ilib/app-scened-template -Ilib/callback-connector -Ilib/u8g2 -Ilib/lfrfid -Ilib/flipper_application -Ilib/music_worker -Ilib/mjs -Ilib/nanopb -Ilib/heatshrink -Ilib/ble_profile -Ilib/bit_lib -Ilib/datetime -Ibuild/f7-firmware-C/.extapps/dolphin_jump -Iapplications_user/dolphin-jump applications_user/dolphin-jump/dolphin_jump.c
arm-none-eabi-gcc -o build/f7-firmware-C/.extapps/dolphin_jump/dolphin_jump_icons.o -c -std=gnu2x -Wstrict-prototypes -Wno-strict-prototypes -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -mthumb -Wall -Wextra -Werror -Wno-error=deprecated-declarations -Wno-address-of-packed-member -Wredundant-decls -Wdouble-promotion -fdata-sections -ffunction-sections -fsingle-precision-constant -fno-math-errno -g -Os -mword-relocations -mlong-calls -fno-common -nostdlib -D_GNU_SOURCE -DFW_CFG_default -D"M_MEMORY_FULL(x)=abort()" -DSTM32WB -DSTM32WB55xx -DUSE_FULL_ASSERT -DUSE_FULL_LL_DRIVER -DMBEDTLS_CONFIG_FILE=\"mbedtls_cfg.h\" -DPB_ENABLE_MALLOC -DFW_ORIGIN_Official -DFURI_NDEBUG -DNDEBUG -DFAP_VERSION=\"0.1\" -Ifuri -Iapplications/services -Iapplications/main -Itargets/furi_hal_include -Itargets/f7/ble_glue -Itargets/f7/fatfs -Itargets/f7/furi_hal -Itargets/f7/inc -I. -Ilib -Ibuild/f7-firmware-C/assets/compiled -Ilib/mlib -Ilib/cmsis_core -Ilib/stm32wb_cmsis/Include -Ilib/stm32wb_hal/Inc -Ilib/stm32wb_copro/wpan -Ilib/drivers -Ilib/FreeRTOS-Kernel/include -Ilib/FreeRTOS-Kernel/portable/GCC/ARM_CM4F -Ilib/FreeRTOS-glue -Ilib/microtar/src -Ilib/mbedtls/include -Ilib/toolbox -Ilib/libusb_stm32/inc -Ilib/drivers -Ilib/flipper_format -Ilib/one_wire -Ilib/ibutton -Ilib/infrared/encoder_decoder -Ilib/infrared/worker -Ilib/littlefs -Ilib/subghz -Ilib/nfc -Ilib/digital_signal -Ilib/pulse_reader -Ilib/signal_reader -Ilib/app-scened-template -Ilib/callback-connector -Ilib/u8g2 -Ilib/lfrfid -Ilib/flipper_application -Ilib/music_worker -Ilib/mjs -Ilib/nanopb -Ilib/heatshrink -Ilib/ble_profile -Ilib/bit_lib -Ilib/datetime -Ibuild/f7-firmware-C/.extapps/dolphin_jump -Iapplications_user/dolphin-jump build/f7-firmware-C/.extapps/dolphin_jump/dolphin_jump_icons.c
Using tempfile /var/folders/mj/qp601k_s0rx3cwsv6chm7_6h0000gn/T/tmp_yi0ce9y.lnk for command line:
arm-none-eabi-g++ -o build/f7-firmware-C/.extapps/dolphin_jump_d.elf -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 -mlittle-endian -mthumb -Wl,--no-warn-rwx-segment -Wl,--wrap,fflush -Wl,--wrap,fflush_unlocked -Wl,--wrap,_fflush_r -Wl,--wrap,_fflush_unlocked_r -Wl,--wrap,printf -Wl,--wrap,printf_unlocked -Wl,--wrap,_printf_r -Wl,--wrap,_printf_unlocked_r -Wl,--wrap,putc -Wl,--wrap,putc_unlocked -Wl,--wrap,_putc_r -Wl,--wrap,_putc_unlocked_r -Wl,--wrap,putchar -Wl,--wrap,putchar_unlocked -Wl,--wrap,_putchar_r -Wl,--wrap,_putchar_unlocked_r -Wl,--wrap,puts -Wl,--wrap,puts_unlocked -Wl,--wrap,_puts_r -Wl,--wrap,_puts_unlocked_r -Wl,--wrap,snprintf -Wl,--wrap,snprintf_unlocked -Wl,--wrap,_snprintf_r -Wl,--wrap,_snprintf_unlocked_r -Wl,--wrap,vsnprintf -Wl,--wrap,vsnprintf_unlocked -Wl,--wrap,_vsnprintf_r -Wl,--wrap,_vsnprintf_unlocked_r -Wl,--wrap,__assert -Wl,--wrap,__assert_unlocked -Wl,--wrap,___assert_r -Wl,--wrap,___assert_unlocked_r -Wl,--wrap,__assert_func -Wl,--wrap,__assert_func_unlocked -Wl,--wrap,___assert_func_r -Wl,--wrap,___assert_func_unlocked_r -Wl,--wrap,setbuf -Wl,--wrap,setbuf_unlocked -Wl,--wrap,_setbuf_r -Wl,--wrap,_setbuf_unlocked_r -Wl,--wrap,setvbuf -Wl,--wrap,setvbuf_unlocked -Wl,--wrap,_setvbuf_r -Wl,--wrap,_setvbuf_unlocked_r -Wl,--wrap,fprintf -Wl,--wrap,fprintf_unlocked -Wl,--wrap,_fprintf_r -Wl,--wrap,_fprintf_unlocked_r -Wl,--wrap,vfprintf -Wl,--wrap,vfprintf_unlocked -Wl,--wrap,_vfprintf_r -Wl,--wrap,_vfprintf_unlocked_r -Wl,--wrap,vprintf -Wl,--wrap,vprintf_unlocked -Wl,--wrap,_vprintf_r -Wl,--wrap,_vprintf_unlocked_r -Wl,--wrap,fputc -Wl,--wrap,fputc_unlocked -Wl,--wrap,_fputc_r -Wl,--wrap,_fputc_unlocked_r -Wl,--wrap,fputs -Wl,--wrap,fputs_unlocked -Wl,--wrap,_fputs_r -Wl,--wrap,_fputs_unlocked_r -Wl,--wrap,sprintf -Wl,--wrap,sprintf_unlocked -Wl,--wrap,_sprintf_r -Wl,--wrap,_sprintf_unlocked_r -Wl,--wrap,asprintf -Wl,--wrap,asprintf_unlocked -Wl,--wrap,_asprintf_r -Wl,--wrap,_asprintf_unlocked_r -Wl,--wrap,vasprintf -Wl,--wrap,vasprintf_unlocked -Wl,--wrap,_vasprintf_r -Wl,--wrap,_vasprintf_unlocked_r -Wl,--wrap,asiprintf -Wl,--wrap,asiprintf_unlocked -Wl,--wrap,_asiprintf_r -Wl,--wrap,_asiprintf_unlocked_r -Wl,--wrap,asniprintf -Wl,--wrap,asniprintf_unlocked -Wl,--wrap,_asniprintf_r -Wl,--wrap,_asniprintf_unlocked_r -Wl,--wrap,asnprintf -Wl,--wrap,asnprintf_unlocked -Wl,--wrap,_asnprintf_r -Wl,--wrap,_asnprintf_unlocked_r -Wl,--wrap,diprintf -Wl,--wrap,diprintf_unlocked -Wl,--wrap,_diprintf_r -Wl,--wrap,_diprintf_unlocked_r -Wl,--wrap,fiprintf -Wl,--wrap,fiprintf_unlocked -Wl,--wrap,_fiprintf_r -Wl,--wrap,_fiprintf_unlocked_r -Wl,--wrap,iprintf -Wl,--wrap,iprintf_unlocked -Wl,--wrap,_iprintf_r -Wl,--wrap,_iprintf_unlocked_r -Wl,--wrap,siprintf -Wl,--wrap,siprintf_unlocked -Wl,--wrap,_siprintf_r -Wl,--wrap,_siprintf_unlocked_r -Wl,--wrap,sniprintf -Wl,--wrap,sniprintf_unlocked -Wl,--wrap,_sniprintf_r -Wl,--wrap,_sniprintf_unlocked_r -Wl,--wrap,vasiprintf -Wl,--wrap,vasiprintf_unlocked -Wl,--wrap,_vasiprintf_r -Wl,--wrap,_vasiprintf_unlocked_r -Wl,--wrap,vasniprintf -Wl,--wrap,vasniprintf_unlocked -Wl,--wrap,_vasniprintf_r -Wl,--wrap,_vasniprintf_unlocked_r -Wl,--wrap,vasnprintf -Wl,--wrap,vasnprintf_unlocked -Wl,--wrap,_vasnprintf_r -Wl,--wrap,_vasnprintf_unlocked_r -Wl,--wrap,vdiprintf -Wl,--wrap,vdiprintf_unlocked -Wl,--wrap,_vdiprintf_r -Wl,--wrap,_vdiprintf_unlocked_r -Wl,--wrap,vfiprintf -Wl,--wrap,vfiprintf_unlocked -Wl,--wrap,_vfiprintf_r -Wl,--wrap,_vfiprintf_unlocked_r -Wl,--wrap,viprintf -Wl,--wrap,viprintf_unlocked -Wl,--wrap,_viprintf_r -Wl,--wrap,_viprintf_unlocked_r -Wl,--wrap,vsiprintf -Wl,--wrap,vsiprintf_unlocked -Wl,--wrap,_vsiprintf_r -Wl,--wrap,_vsiprintf_unlocked_r -Wl,--wrap,vsniprintf -Wl,--wrap,vsniprintf_unlocked -Wl,--wrap,_vsniprintf_r -Wl,--wrap,_vsniprintf_unlocked_r -specs=nano.specs -Wl,--gc-sections -Wl,--undefined=uxTopUsedPriority -Wl,--wrap,_malloc_r -Wl,--wrap,_free_r -Wl,--wrap,_calloc_r -Wl,--wrap,_realloc_r -n -Xlinker -Map=build/f7-firmware-C/.extapps/dolphin_jump_d.elf.map -Ttargets/f7/application_ext.ld -Ur -Wl,-Ur -nostartfiles -mlong-calls -fno-common -nostdlib -Wl,--no-export-dynamic -fvisibility=hidden -Wl,-edolphin_jump_app build/f7-firmware-C/.extapps/dolphin_jump/Game.o build/f7-firmware-C/.extapps/dolphin_jump/dolphin_jump.o build/f7-firmware-C/.extapps/dolphin_jump/main.o build/f7-firmware-C/.extapps/dolphin_jump/dolphin_jump_icons.o -Lbuild/f7-firmware-C/lib -lm -lgcc -lstdc++ -lsupc++
arm-none-eabi-g++ @/var/folders/mj/qp601k_s0rx3cwsv6chm7_6h0000gn/T/tmp_yi0ce9y.lnk
API version 69.0 is up to date
prepare_app_metadata(["build/f7-firmware-C/.extapps/dolphin_jump.fap", "build/f7-firmware-C/.extapps/dolphin_jump/.fapmeta"], ["build/f7-firmware-C/.extapps/dolphin_jump_d.elf"])
arm-none-eabi-objcopy --remove-section .ARM.attributes --add-section .fapmeta=build/f7-firmware-C/.extapps/dolphin_jump/.fapmeta --set-section-flags .fapmeta=contents,noload,readonly,data --strip-debug --strip-unneeded --add-gnu-debuglink=build/f7-firmware-C/.extapps/dolphin_jump_d.elf build/f7-firmware-C/.extapps/dolphin_jump_d.elf build/f7-firmware-C/.extapps/dolphin_jump.fap
python3 scripts/fastfap.py build/f7-firmware-C/.extapps/dolphin_jump.fap arm-none-eabi-objcopy
_validate_app_imports(["build/f7-firmware-C/.extapps/dolphin_jump.impsyms"], ["build/f7-firmware-C/.extapps/dolphin_jump.fap"])
```

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
