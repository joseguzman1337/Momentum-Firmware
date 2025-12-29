# Contributing to RTL8814AU macOS Driver

Thank you for your interest in contributing to this project!

## Code of Conduct

This project follows a code of conduct that ensures a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- macOS version
- Hardware information (USB adapter model)
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant logs (see README for how to capture logs)

### Suggesting Features

Feature requests are welcome! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- How it might work

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass (`./build.sh && xcodebuild test ...`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Use Swift 6.0 features and modern Swift concurrency (async/await, actors)
- Follow Apple's Swift style guide
- Add documentation comments for public APIs
- Use meaningful variable and function names
- Keep functions focused and small
- Add unit tests for new functionality

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb ("Add", "Fix", "Update", "Remove")
- Keep the first line under 72 characters
- Add detailed description if needed after a blank line

Example:
```
Add support for WPA3 encryption

- Implement SAE handshake
- Add WPA3-SAE capability detection
- Update WiFi interface to handle WPA3 frames
```

## Development Setup

1. Install prerequisites:
   ```bash
   brew install swift cmake
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rtl8814au-macos-driver
   cd rtl8814au-macos-driver
   ```

3. Configure code signing:
   ```bash
   cp CodeSigning.xcconfig.example CodeSigning.xcconfig
   # Edit CodeSigning.xcconfig with your Team ID
   ```

4. Build:
   ```bash
   ./build.sh
   ```

## Testing

### Unit Tests

Run unit tests with:
```bash
xcodebuild test -project RTL8814AUDriver.xcodeproj -scheme RTL8814AUDriverTests
```

### Manual Testing

1. Build and install the driver
2. Plug in RTL8814AU device
3. Check System Settings > Network
4. Try connecting to a WiFi network
5. Monitor logs for errors:
   ```bash
   log stream --predicate 'subsystem == "com.rtl8814au.driver"'
   ```

## Project Structure

```
.
├── RTL8814AUDriver/      # Main driver (DriverKit extension)
│   ├── Driver.swift      # Entry point
│   ├── USBInterface.swift # USB communication
│   └── WiFiInterface.swift # WiFi protocol
├── RTL8814AUApp/         # Helper app for installation
├── Shared/               # Shared code
├── Tests/                # Unit tests
└── Scripts/              # Build and install scripts
```

## Areas Needing Help

- [ ] Firmware integration (actual RTL8814AU firmware binary)
- [ ] WPA3 support
- [ ] Advanced 802.11ac features (beamforming, MU-MIMO)
- [ ] Power management
- [ ] Performance optimization
- [ ] Testing on various hardware
- [ ] Documentation improvements

## Resources

- [Apple DriverKit Documentation](https://developer.apple.com/documentation/driverkit)
- [IOKit Fundamentals](https://developer.apple.com/library/archive/documentation/DeviceDrivers/Conceptual/IOKitFundamentals/)
- [Realtek RTL8814AU Datasheet](https://www.realtek.com) (if available)
- [802.11 Standards](https://www.ieee802.org/11/)

## License

By contributing, you agree that your contributions will be licensed under the GPL-2.0 License.

## Questions?

Feel free to open an issue for questions or discussions!
