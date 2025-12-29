# Contributing to RTL8814AU macOS Driver

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows a code of conduct that we expect all contributors to adhere to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept differing viewpoints gracefully
- Show empathy towards others

## Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork yourusername/rtl8814au-macos
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rtl8814au-macos.git
   cd rtl8814au-macos
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/yourusername/rtl8814au-macos.git
   ```

## Development Setup

### Prerequisites

- macOS Sequoia (15.0+)
- Xcode 16.0+
- Swift 5.9+
- Homebrew
- Apple Developer account (for testing)

### Environment Setup

```bash
# Install development tools
brew install swift-format
brew install swiftlint

# Enable developer mode for system extensions
sudo systemextensionsctl developer on
```

### Building

```bash
./build.sh
```

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check existing issues
2. Update to the latest version
3. Collect system information

When reporting:
```markdown
**Description**: Clear description of the bug

**Steps to Reproduce**:
1. Step one
2. Step two
3. ...

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- macOS version:
- Driver version:
- Hardware:
- Logs: (attach relevant logs)
```

### Suggesting Features

Use the feature request template:
```markdown
**Feature Description**: Clear description

**Use Case**: Why is this needed?

**Proposed Implementation**: How could this work?

**Alternatives**: Other approaches considered
```

### Code Contributions

We welcome contributions in these areas:

- **Bug fixes**: Fix existing issues
- **Features**: Add new functionality
- **Documentation**: Improve docs
- **Tests**: Add test coverage
- **Performance**: Optimize code

## Coding Standards

### Swift Style Guide

Follow Apple's [Swift API Design Guidelines](https://swift.org/documentation/api-design-guidelines/).

Key points:
- Use clear, descriptive names
- Prefer clarity over brevity
- Follow Swift naming conventions
- Document public APIs

### Code Formatting

```bash
# Format code
swift-format -i -r RTL8814AUDriver/

# Lint code
swiftlint
```

### File Structure

```swift
// Copyright and license header

import Foundation
import DriverKit

/// Documentation for class/struct
class ClassName {
    
    // MARK: - Properties
    
    private var property: Type
    
    // MARK: - Initialization
    
    init() {
        // ...
    }
    
    // MARK: - Public Methods
    
    func publicMethod() {
        // ...
    }
    
    // MARK: - Private Methods
    
    private func privateMethod() {
        // ...
    }
}
```

### Logging

Use structured logging with appropriate levels:

```swift
os_log("Informational message", type: .info)
os_log("Debug information: %{public}@", type: .debug, value)
os_log("Warning: %{public}@", type: .default, warning)
os_log("Error: %{public}@", type: .error, error)
```

### Error Handling

```swift
// Define clear error types
enum DriverError: Error, LocalizedError {
    case descriptiveName(details: String)
    
    var errorDescription: String? {
        // Provide helpful messages
    }
}

// Use Result type for fallible operations
func operation() -> Result<Success, DriverError> {
    // ...
}

// Use throws for expected errors
func operation() throws -> Success {
    // ...
}
```

## Testing

### Writing Tests

```swift
import Testing
@testable import RTL8814AUDriver

@Suite("Driver Initialization Tests")
struct DriverInitializationTests {
    
    @Test("Driver initializes with valid device")
    func testValidDeviceInit() async throws {
        let driver = RTL8814AUDriver()
        // Test implementation
    }
    
    @Test("Driver fails with invalid device")
    func testInvalidDeviceInit() async throws {
        // Test implementation
        #expect(throws: DriverError.unsupportedDevice) {
            // Code that should throw
        }
    }
}
```

### Running Tests

```bash
# Run all tests
swift test

# Run specific test
swift test --filter DriverInitializationTests

# Run with coverage
swift test --enable-code-coverage
```

### Hardware Testing

For hardware-specific features:

1. Document test hardware used
2. Provide clear test steps
3. Include expected results
4. Note any device-specific behavior

## Pull Request Process

### Before Submitting

- [ ] Code builds without errors
- [ ] All tests pass
- [ ] Code is formatted and linted
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### Commit Messages

Follow conventional commits:

```
type(scope): brief description

Detailed explanation of what changed and why.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code builds
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Follows style guide
```

### Review Process

1. Submit PR with clear description
2. Automated checks run (CI/CD)
3. Maintainer reviews code
4. Address feedback
5. Approval and merge

## Development Guidelines

### DriverKit Best Practices

```swift
// Use async/await for DriverKit APIs
func start(provider: IOService) async throws {
    try await super.start(provider: provider)
    // Driver initialization
}

// Proper cleanup
func stop(provider: IOService) async {
    cleanup()
    await super.stop(provider: provider)
}

// Handle device removal gracefully
```

### USB Communication

```swift
// Use proper error handling
guard let pipe = bulkOutPipe else {
    throw DriverError.endpointNotAvailable
}

// Async USB operations
try await withCheckedThrowingContinuation { continuation in
    let result = pipe.write(buffer, length: size) { _, error in
        if error == kIOReturnSuccess {
            continuation.resume()
        } else {
            continuation.resume(throwing: DriverError.transmissionFailed)
        }
    }
}
```

### Memory Management

```swift
// Use weak references to avoid cycles
private weak var driver: RTL8814AUDriver?

// Clean up resources
deinit {
    cleanup()
}

// Proper buffer management
var buffer = Data(count: size)
buffer.withUnsafeMutableBytes { ptr in
    // Use buffer
}
```

## Documentation

### Code Documentation

```swift
/// Brief description of function
///
/// Detailed explanation of what this does,
/// when to use it, and any important notes.
///
/// - Parameters:
///   - param1: Description of parameter
///   - param2: Description of parameter
/// - Returns: Description of return value
/// - Throws: `DriverError.specific` when condition occurs
func documentedFunction(param1: Type, param2: Type) throws -> ReturnType {
    // Implementation
}
```

### User Documentation

When adding features, update:
- README.md: User-facing features
- BUILDING.md: Build process changes
- Wiki: Detailed guides

## Release Process

Maintainers follow this process for releases:

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build and sign release
6. Create GitHub release
7. Update Homebrew formula
8. Announce release

## Questions?

- Open a [Discussion](https://github.com/yourusername/rtl8814au-macos/discussions)
- Check the [Wiki](https://github.com/yourusername/rtl8814au-macos/wiki)
- Review existing [Issues](https://github.com/yourusername/rtl8814au-macos/issues)

Thank you for contributing! 🎉
