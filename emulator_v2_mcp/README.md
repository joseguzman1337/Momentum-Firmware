# Momentum Emulator v2 MCP

Servidor MCP por `stdio` que conecta clientes de IA con el Emulator v2 de este
repositorio. No abre hardware. La ruta funcional usa el motor STM32 compilado y el runner canónico
[`tools/flipper_emulator/runner.py`](../tools/flipper_emulator/runner.py). No
enumera USB/serie, no abre hardware físico y nunca flashea el Flipper.

## Límites honestos

- CPU1 Cortex-M4 ejecuta el firmware compilado en el motor nativo.
- Pantalla y botones se obtienen/controlan mediante los eventos y el canal de
  control de una ejecución nativa identificada por `run_id`.
- CPU2, FUS y radio son estados/replay determinista; no ejecutan el Cortex-M0+
  ni producen RF.
- El RPC USB expone lectura del almacenamiento interno persistente sanitizado;
  no inventa una operación remota de escritura que el backend no implemente.
- USB/RPC usa un PTY del host; no ejecuta el periférico USB del STM32.
- El framebuffer nativo se expone aunque una captura oracle concreta no
  coincida píxel por píxel; esa comparación diferencial se reporta aparte.
- Option bytes son de solo lectura. La OTP y cualquier identidad son sintéticas
  o sanitizadas.
- El modelo Python auxiliar sirve para pruebas unitarias; no se presenta como
  ejecución del firmware.

## Arranque

```sh
cd /Volumes/h101/Momentum-Firmware/emulator_v2_mcp
python3 flipper_mcp_server.py
```

Los scripts instalados fuera del checkout usan
`MOMENTUM_FIRMWARE_ROOT=/Volumes/h101/Momentum-Firmware` para localizar el
runner, firmware y artefactos canónicos.

La configuración lista para importar está en
[`../.ai/mcp/emulator_v2_mcp.json`](../.ai/mcp/emulator_v2_mcp.json).

## Protocolo y herramientas

El servidor implementa JSON-RPC 2.0/MCP `2024-11-05` por líneas JSON en
entrada/salida estándar. Expone estas 15 herramientas:

- `emulator_capabilities`
- `emulator_validate_spec`
- `emulator_validate_artifact`
- `emulator_run`
- `emulator_run_status`
- `emulator_events`
- `emulator_report`
- `emulator_snapshot_metadata`
- `emulator_screen`
- `emulator_input`
- `emulator_storage_list`
- `emulator_storage_read`
- `emulator_usb_rpc`
- `model_storage_list` (modelo Python explícito)
- `model_storage_read` (modelo Python explícito)

Primero se inicia una ejecución con `emulator_run` y un spec JSON. Las
operaciones nativas de pantalla/entrada usan el `run_id` devuelto. El spec puede
incluir `live_control: true` para crear un FIFO aislado que reenvía botones a la
entrada estándar del motor mientras el proceso está activo. Los eventos se
publican incrementalmente en `events.jsonl` y el estado en
`runtime-status.json`.

Spec mínimo:

```json
{
  "firmware": "/Volumes/h101/Momentum-Firmware/build/f7-firmware-C/firmware.bin",
  "output": "/Volumes/h101/Momentum-Firmware/.ai/logs/qemu-fw/mcp-run",
  "max_instructions": 250000000,
  "live_control": true
}
```

## Verificación

```sh
python3 -m unittest -v tests.emulator_v2_mcp.test_mcp_integration
```

La aceptación ejecuta el motor STM32 compilado con el firmware actual durante
250 millones de instrucciones; un script o backend falso no satisface esa
prueba. También verifica `initialize`, `tools/list`, `tools/call`, aislamiento
de rutas, recursos, reportes y eventos.

La matriz completa está materializada en
[`../.ai/logs/qemu-fw/mcp-full-feature-250m.spec.json`](../.ai/logs/qemu-fw/mcp-full-feature-250m.spec.json):
firmware y motor reales, snapshot sanitizado, fixture SD, referencia pública C2
no ejecutada, USB/RPC virtual, almacenamiento persistente y control en vivo. El
resultado verificable se guarda en
[`../.ai/logs/qemu-fw/mcp-full-feature-health.json`](../.ai/logs/qemu-fw/mcp-full-feature-health.json).
