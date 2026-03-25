# Web Fetch Examples for Momentum Firmware

## Common Research Tasks

### 1. Documentation Analysis
```bash
# In Gemini CLI
/research https://docs.flipper.net/development/hardware

# Command line
./scripts/web-research.sh docs
```

### 2. Security Research
```bash
# Firmware security best practices
./scripts/web-research.sh security

# Specific vulnerability research
gemini --prompt "web_fetch(prompt='Analyze security vulnerabilities in https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=firmware and provide mitigation strategies')"
```

### 3. API Documentation
```bash
# Flipper Zero API reference
./scripts/web-research.sh api https://developer.flipper.net/flipperzero/doxygen/

# Third-party library docs
./scripts/web-research.sh api https://github.com/flipperdevices/flipperzero-firmware/wiki
```

### 4. Comparative Analysis
```bash
# Compare firmware approaches
./scripts/web-research.sh compare https://github.com/DarkFlippers/unleashed-firmware https://github.com/RogueMaster/flipperzero-firmware-wPlugins

# Compare hardware specs
gemini --prompt "web_fetch(prompt='Compare hardware specifications from https://docs.flipper.net/basics/hardware and https://www.st.com/en/microcontrollers-microprocessors/stm32wb55rg.html')"
```

### 5. Community Insights
```bash
# Gather community discussions
./scripts/web-research.sh community

# Specific forum research
gemini --prompt "web_fetch(prompt='Summarize firmware development tips from https://forum.flipper.net/c/development/7')"
```

## Advanced Web Fetch Patterns

### Multi-URL Analysis
```bash
gemini --prompt "web_fetch(prompt='Compare SubGHz implementations from https://github.com/flipperdevices/flipperzero-firmware/tree/dev/applications/main/subghz and https://github.com/Next-Flip/Momentum-Firmware/tree/dev/applications/main/subghz, highlighting key differences')"
```

### Technical Documentation
```bash
gemini --prompt "web_fetch(prompt='Extract C programming patterns from https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/CodingStyle.md and provide examples for Momentum Firmware')"
```

### Issue Research
```bash
gemini --prompt "web_fetch(prompt='Analyze recent issues from https://github.com/flipperdevices/flipperzero-firmware/issues?q=is%3Aissue+is%3Aopen+label%3Abug and identify patterns relevant to Momentum Firmware')"
```

## Research Output Structure

All research is saved to `research/` directory:
- `flipper-docs.md` - Official documentation summaries
- `security-practices.md` - Security best practices
- `api-*.md` - API documentation analysis
- `comparison.md` - Comparative analysis results
- `community-insights.md` - Community discussions

## Best Practices

1. **Specific Prompts**: Include clear instructions for what to extract
2. **Multiple Sources**: Compare information from different sources
3. **Context Relevance**: Focus on Flipper Zero and embedded systems
4. **Actionable Insights**: Request implementation examples and code patterns
5. **Regular Updates**: Refresh research as documentation evolves