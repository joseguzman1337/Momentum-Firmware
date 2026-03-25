---
name: subghz-analyzer
description: Analyze and work with Sub-GHz protocols in Momentum Firmware
metadata:
  short-description: Sub-GHz protocol analysis and development
---

# Sub-GHz Analyzer

Analyze and work with Sub-GHz protocols in Momentum Firmware, including protocol development and signal analysis.

## Context

- Momentum Firmware supports extended Sub-GHz frequencies (281-962 MHz)
- Uses CC1101 transceiver for Sub-GHz communication
- Protocols are defined in `lib/subghz/protocols/`
- Signal analysis tools available in external apps

## Protocol Structure

Sub-GHz protocols in Momentum follow this pattern:

```c
typedef struct {
    SubGhzProtocolDecoderBase base;
    SubGhzBlockDecoder decoder;
    SubGhzBlockGeneric generic;
    // Protocol-specific fields
} SubGhzProtocolDecoderProtocolName;
```

## Key Components

1. **Protocol Registry:**
   - Located in `lib/subghz/subghz_protocol_registry.h`
   - Registers all available protocols
   - Handles protocol selection and initialization

2. **Signal Processing:**
   - Raw signal capture and analysis
   - Manchester/PWM decoding
   - Bit extraction and validation

3. **File Formats:**
   - `.sub` files store captured signals
   - Flipper Format for structured data
   - Raw signal data for analysis

## Analysis Process

1. **Capture Signal:**
   - Use Sub-GHz app to record unknown signals
   - Save as raw format for analysis
   - Note frequency, modulation, and timing

2. **Analyze Pattern:**
   - Look for repeating patterns
   - Identify sync/preamble sequences
   - Determine bit encoding (Manchester, PWM, etc.)

3. **Extract Data:**
   - Parse bit stream for meaningful data
   - Identify fixed vs. variable portions
   - Look for checksums or validation

4. **Create Protocol:**
   - Implement decoder following existing patterns
   - Add encoder if transmission needed
   - Register in protocol registry

## Development Tools

- `applications/external/sub_analyzer/` - Signal analysis app
- `applications/external/protoview/` - Protocol viewer
- CLI tools for raw signal processing
- Spectrum analyzer for frequency analysis

## Testing

- Test with known good signals first
- Verify decoding accuracy
- Test edge cases and noise handling
- Validate against original equipment