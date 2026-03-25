# Codex Slack Integration

## Quick Setup

1. **Prerequisites**: Ensure you have a ChatGPT Plus/Pro/Business/Enterprise plan
2. **Run setup**: `./ai/codex/setup_slack.sh`
3. **Install Slack app**: Visit [Codex settings](https://chatgpt.com/codex/settings/connectors)
4. **Add to channels**: Mention `@Codex` in your Slack channels

## Usage Examples

```
@Codex fix the memory leak in applications/main/nfc/
@Codex optimize the SubGHz protocol handling
@Codex review changes in the BadUSB implementation
@Codex add error handling to the file browser
```

## Environment Detection

Codex automatically detects the Momentum Firmware environment based on:
- Keywords: firmware, flipper, momentum, embedded
- File patterns: *.c, *.h, *.py, fbt files
- Repository context: joseguzman1337/Momentum-Firmware

## Integration Features

- **Auto-acknowledgment**: 👀 emoji response
- **Environment selection**: Automatic routing to momentum-firmware environment  
- **Task tracking**: Direct links to Codex Cloud Tasks
- **Thread context**: Maintains conversation history

## Troubleshooting

- **Missing connections**: Follow Slack prompts to reconnect
- **Wrong environment**: Reply with "Please run this in momentum-firmware"
- **Complex requests**: Summarize key details in your latest message