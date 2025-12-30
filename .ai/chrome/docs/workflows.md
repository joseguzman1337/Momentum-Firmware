# Chrome Integration Workflows for Momentum Firmware

## Quick Setup
```bash
./scripts/setup-chrome-integration.sh
claude --chrome
```

## Common Workflows

### Test Local Build
```
Open localhost:8080, navigate through the main menu, test animations, 
and check console for any errors
```

### Review Documentation
```
Go to momentum-fw.dev, check the asset packs page loads correctly,
and verify all download links work
```

### GitHub PR Review
```
Open the latest PR on github.com/joseguzman1337/Momentum-Firmware,
check the diff, run any linked tests, and summarize the changes
```

### Debug Web Updater
```
Go to momentum-fw.dev/update, test the connection flow with a mock
device, and check for any console errors during the update process
```

### Asset Pack Testing
```
Download an asset pack from momentum-fw.dev/asset-packs, verify
the file structure, and test installation instructions
```

## Browser Commands
- `/chrome` - Check connection status
- Record demos: "Record a GIF showing the web updater flow"
- Extract data: "Get all asset pack names and descriptions from the website"
- Form testing: "Test the contact form with invalid data"