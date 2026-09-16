# Flipper Zero Emulator v2 (Target: F7B9C6 — Unit emulator-v2) with MCP Server

Un emulador completo, determinista y modular del **Flipper Zero** para arquitecturas basadas en el microcontrolador **STM32WB55RG**, calibrado con el perfil de hardware y datos de la unidad física **emulator-v2** (F7B9C6, Target 7, Región Colombia CO, OTP v2).

Incluye un servidor nativo **Model Context Protocol (MCP)** para permitir que asistentes de IA (Claude Desktop, Cursor, Gemini CLI, Windsurf, etc.) controlen el emulador directamente mediante llamadas a herramientas, lean la pantalla ST7567, ejecuten comandos CLI y simulen protocolos de radiofrecuencia (Sub-GHz, NFC, RFID).

---

## 1. Características Principales

1. **Núcleo y Memoria STM32WB55RG:**
   - **CPU1:** ARM Cortex-M4 @ 64 MHz con modelo de registros R0-R15, xPSR, SP (MSP/PSP) y excepciones.
   - **NVIC:** Controlador vectorial de interrupciones con reubicación VTOR y prioridades.
   - **SysTick & DWT:** Temporizador periódico de 24 bits (tick de 1 ms para FuriOS) y contador de ciclos DWT CYCCNT.
   - **RCC & RTC:** Árbol de reloj (HSE 32 MHz, LSE 32.768 kHz, PLL 64 MHz) y calendario BCD en tiempo real.
   - **Mapa de Memoria:** Flash (1 MB), SRAM1 (192 KB), SRAM2A (32 KB), SRAM2B (32 KB) y enrutador MMIO.
   - **HSEM & IPCC:** 32 semáforos por hardware y 6 canales de comunicación bidireccional entre núcleos.
   - **Coprocesador CPU2:** Emulación de radio stack v1.20.0 y FUS v1.2.0 con respuestas SHCI/HCI.

2. **Periféricos e Interfaces Flipper Zero:**
   - **Pantalla ST7567:** LCD monocromática de 128×64 píxeles sobre SPI con renderizador ASCII en tiempo real y exportación de framebuffer (PBM/base64).
   - **Entradas:** D-Pad de 5 posiciones (Up, Down, Left, Right, OK) + botón Back, con gestión de eventos (Press, Release, Short, Long).
   - **Almacenamiento Interno `/int`:** Flash persistente inicializada con los archivos reales sanitizados de la unidad (`.dolphin.state`, `.bt.settings`, `.desktop.settings`, `.region_data`, etc.).
   - **Almacenamiento `/ext`:** MicroSD virtual sobre SPI2 con sistema de archivos FAT y estructura de carpetas (`subghz`, `nfc`, `lfrfid`, `ibutton`, `infrared`, `badusb`, `apps`).
   - **Sub-GHz (TI CC1101):** Transceptor 300–928 MHz con filtrado de frecuencias por región (CO: 433 MHz, 915 MHz), transmisión de claves y tramas RAW.
   - **NFC & RFID (ST25R3916 + 125 kHz):** Lectura y emulación de tarjetas Mifare Classic, NTAG215 y tags RFID EM4100 / HIDProx.
   - **Audio & Vibración:** Sintetizador PWM vía TIM16, motor de vibración y LED de notificación RGB.
   - **USB CDC Virtual & CLI:** Shell interactivo completo con comandos oficiales (`device_info`, `date`, `ps`, `free`, `power info`, `storage list`, etc.).
   - **Protocolo RPC Protobuf:** Manejador para comunicación con herramientas oficiales (Ping, DeviceInfo, VirtualDisplay, Storage).

3. **Integración MCP (Model Context Protocol):**
   - Servidor estándar JSON-RPC 2.0 sobre `stdio` según especificación MCP 2024-11-05.
   - 16 herramientas expuestas (`flipper_info`, `flipper_press_button`, `flipper_get_screen`, `flipper_cli_exec`, `flipper_subghz_tx`, `flipper_nfc_read`, etc.).
   - Recursos en vivo (`flipper://screen/current`, `flipper://device/info`, `flipper://storage/manifest`).

---

## 2. Estructura del Proyecto

```
flipper_emulator_project/
├── flipper_mcp_server.py                # Entrada ejecutable del servidor MCP
├── main.py                              # Lanzador y CLI interactivo
├── run_tests.py                         # Suite de pruebas automatizadas
├── requirements.txt                     # Requisitos (estándar puro sin dependencias obligatorias)
├── pyproject.toml                       # Configuración de paquete Python
├── setup.py                             # Instalador estándar
├── sd_card/                             # Raíz de la tarjeta MicroSD virtual (/ext)
│   └── ext/
│       ├── subghz/                      # Archivos .sub (Garage_Door, RAW)
│       ├── nfc/                         # Archivos .nfc (Mifare Classic, NTAG)
│       ├── lfrfid/                      # Archivos .rfid (EM4100, HID)
│       ├── ibutton/                     # Llaves iButton .ibtn
│       ├── infrared/                    # Controles infrarrojos .ir
│       ├── badusb/                      # Scripts Ducky .txt
│       └── apps/                        # Aplicaciones FAP
└── tools/
    └── flipper_emulator/
        ├── __init__.py
        ├── emulator.py                  # Motor central unificado del emulador
        ├── models.py                    # Estructuras de datos, constantes y perfil emulator-v2
        ├── runner.py                    # Arnés de pruebas y verificación de hashes
        ├── COVERAGE.md                  # Matriz de cobertura de subsistemas
        ├── hardware/
        │   ├── cortex_m4.py             # Núcleo CPU Cortex-M4
        │   ├── stm32wb55.py             # Bus del sistema y mapa de memoria
        │   ├── nvic.py                  # Controlador de interrupciones
        │   ├── systick_dwt.py           # SysTick y contador de ciclos DWT
        │   ├── rcc_rtc.py               # Gestión de reloj y RTC
        │   ├── hsem_ipcc.py             # Semáforos HSEM y buzón IPCC
        │   ├── wireless_cpu2.py         # Coprocesador radio y FUS
        │   ├── st7567.py                # Controlador de pantalla LCD 128x64
        │   ├── gpio_buttons.py          # Botones y navegación gráfica
        │   ├── spi_sd.py                # Tarjeta MicroSD virtual
        │   ├── audio_vibro.py           # Buzzer y vibrador
        │   ├── cc1101.py                # Transceptor Sub-GHz
        │   ├── st25r3916.py             # NFC y LF-RFID
        │   └── power_ic.py              # Gestión de energía y batería
        ├── internal_flash/
        │   ├── flash_manager.py         # Almacenamiento persistente /int
        │   ├── otp.py                   # Memoria OTP sintética v2
        │   ├── infotable.py             # InfoTable de Furi HAL
        │   └── fixtures/                # Archivos de configuración de la unidad
        ├── usb/
        │   ├── cdc_acm.py               # Shell CLI serie virtual
        │   ├── rpc_protobuf.py          # Manejador Protobuf RPC
        │   └── pty_transport.py         # Transporte PTY para puerto serie
        ├── oracle/
        │   └── oracle_v2.py             # Datos oráculo de referencia
        └── mcp/
            └── server.py                # Servidor Model Context Protocol (MCP)
```

---

## 3. Uso Rápido

### Requisitos
- Python 3.8 o superior (no requiere librerías externas para funcionar).

### Ejecutar las Pruebas
Para verificar la integridad y funcionamiento de todos los subsistemas:
```bash
python3 run_tests.py
```

### Iniciar la Consola Interactiva
```bash
python3 main.py
```
Comandos útiles en la consola interactiva:
- `help`: Lista de comandos disponibles.
- `screen`: Muestra la pantalla LCD 128x64 en formato ASCII en el terminal.
- `btn ok`, `btn down`, `btn back`: Presiona botones del Flipper Zero y actualiza la pantalla.
- `device_info`: Muestra los datos de fabricación y firmware de la unidad.
- `storage list /ext`: Lista los archivos en la tarjeta MicroSD virtual.
- `subghz tx 433920000`: Transmite una señal Sub-GHz de prueba.
- `nfc read`: Lee una tarjeta NFC virtual.

---

## 4. Configuración del Servidor MCP

Para conectar este emulador a clientes MCP (como Claude Desktop o Cursor), agrega la configuración correspondiente:

### En `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "flipper-zero": {
      "command": "python3",
      "args": [
        "/ruta/completa/flipper_emulator_project/flipper_mcp_server.py"
      ]
    }
  }
}
```

### Herramientas MCP Disponibles:
1. `flipper_info`: Estado general y especificaciones del dispositivo.
2. `flipper_power`: Consulta de batería, carga y reinicio.
3. `flipper_press_button`: Envío de botones (UP, DOWN, LEFT, RIGHT, OK, BACK) con tipo (SHORT, LONG, PRESS, RELEASE).
4. `flipper_get_screen`: Captura de pantalla actual (ASCII o imagen Base64 PBM).
5. `flipper_cli_exec`: Ejecución directa de comandos en la consola CLI de Flipper.
6. `flipper_storage_list`: Listado de directorios en `/ext` o `/int`.
7. `flipper_storage_read`: Lectura de archivos.
8. `flipper_storage_write`: Escritura de archivos.
9. `flipper_storage_delete`: Eliminación de archivos.
10. `flipper_subghz_tx`: Transmisión de radio Sub-GHz.
11. `flipper_subghz_rx`: Recepción y escaneo Sub-GHz.
12. `flipper_nfc_read`: Lectura de tarjetas NFC.
13. `flipper_nfc_emulate`: Emulación de tarjetas NFC.
14. `flipper_rfid_read`: Lectura de tags RFID 125 kHz.
15. `flipper_sound_and_vibro`: Control de tonos sonoros y motor vibrador.
16. `flipper_run_diagnostics`: Autodiagnóstico completo y verificación de cobertura.
