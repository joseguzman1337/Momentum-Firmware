# Contributing to RTL8814AU Driver Build System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🎯 Ways to Contribute

- 🐛 **Bug Reports**: Report issues you encounter
- 💡 **Feature Requests**: Suggest improvements
- 📝 **Documentation**: Improve docs and guides
- 💻 **Code**: Submit bug fixes or new features
- 🧪 **Testing**: Test on different macOS versions and hardware
- 🤝 **Support**: Help other users in issues/discussions

## 📋 Before Contributing

### System Requirements for Development

- macOS Sequoia 15.0+ (for testing)
- Xcode Command Line Tools
- Swift 5.9+ (for Swift components)
- Bash 5.0+ (for shell scripts)
- Git
- RTL8814AU hardware (for testing)

### Knowledge Requirements

- macOS kernel extension development (helpful)
- Swift programming (for Swift tools)
- Bash scripting (for shell scripts)
- Homebrew formula creation (for brew formula)
- Git and GitHub workflows

## 🔧 Development Setup

1. **Fork the repository**
   ```bash
   # On GitHub, click "Fork"
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rtl8814au-driver-build.git
   cd rtl8814au-driver-build
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Make your changes**
   - Follow code style guidelines (see below)
   - Test thoroughly
   - Update documentation as needed

5. **Test your changes**
   ```bash
   # Run test suite
   swift test
   
   # Test installation
   make check
   make build
   
   # Test scripts
   bash -n install-rtl8814au.sh  # Syntax check
   shellcheck install-rtl8814au.sh  # Linting
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

## 📝 Code Style Guidelines

### Swift Code

- Follow [Swift API Design Guidelines](https://swift.org/documentation/api-design-guidelines/)
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use meaningful variable and function names
- Add documentation comments for public APIs

```swift
/// Brief description of the function
///
/// Detailed explanation if needed
///
/// - Parameter name: Description of parameter
/// - Returns: Description of return value
/// - Throws: Description of errors that can be thrown
func exampleFunction(name: String) throws -> Bool {
    // Implementation
}
```

### Bash Scripts

- Use `#!/bin/bash` shebang
- Set error handling: `set -e`
- Use 4 spaces for indentation
- Quote variables: `"$VARIABLE"`
- Use `[[` instead of `[` for conditionals
- Add comments for complex logic

```bash
#!/bin/bash
set -e

# Function description
function_name() {
    local variable="value"
    
    if [[ "$variable" == "value" ]]; then
        echo "Example"
    fi
}
```

### Makefile

- Use tabs (not spaces) for indentation
- Add `.PHONY` for non-file targets
- Document targets with comments
- Use POSIX-compatible syntax where possible

```makefile
.PHONY: target

## target: Description of what it does
target: dependencies
	@echo "Command"
	command --flag
```

## 🧪 Testing Guidelines

### Automated Tests

Add tests to `RTL8814AUDriverTests.swift`:

```swift
@Test("Description of test")
func testYourFeature() async throws {
    // Arrange
    let input = "test"
    
    // Act
    let result = functionUnderTest(input)
    
    // Assert
    #expect(result == expected, "Failure message")
}
```

### Manual Testing Checklist

Before submitting a PR, test:

- [ ] Installation on fresh system
- [ ] Installation on system with existing driver
- [ ] Uninstallation
- [ ] Verification commands
- [ ] Error handling for common failures
- [ ] Both Intel and Apple Silicon (if possible)
- [ ] With SIP enabled and disabled
- [ ] All menu options in launcher
- [ ] All make targets

### Test Coverage Areas

- System requirement checking
- Dependency installation
- Driver compilation
- Installation process
- Verification
- Uninstallation
- Error conditions
- Edge cases

## 📚 Documentation Guidelines

### README Updates

- Keep README.md up to date with code changes
- Use clear, concise language
- Include examples for new features
- Update troubleshooting section for new issues

### Code Comments

- Explain *why*, not just *what*
- Document non-obvious logic
- Add TODO comments for future improvements
- Reference issue numbers when relevant

```swift
// FIXME: Issue #123 - Handle edge case where...
// TODO: Add support for...
// NOTE: This workaround is needed because...
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(installer): Add support for macOS 16

fix(makefile): Correct architecture detection on Apple Silicon

docs(readme): Update troubleshooting section with USB reset steps

test(swift): Add tests for SIP status detection
```

## 🐛 Bug Reports

When reporting bugs, include:

### System Information
```bash
sw_vers
uname -m
csrutil status
```

### Driver Information
```bash
kextstat | grep rtl8814au
ls -la /Library/Extensions/rtl8814au.kext
```

### USB Device Info
```bash
system_profiler SPUSBDataType | grep -A 10 Realtek
```

### Logs
```bash
log show --predicate 'process == "kernel"' --last 5m | grep -i rtl
```

### Steps to Reproduce

1. Step one
2. Step two
3. Expected result
4. Actual result

## 💡 Feature Requests

When suggesting features:

1. **Describe the problem** you're trying to solve
2. **Propose a solution** (if you have one)
3. **Explain the benefit** to users
4. **Consider alternatives** that might exist

## 🔍 Code Review Process

Pull requests will be reviewed for:

- **Functionality**: Does it work as intended?
- **Code quality**: Is it readable and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Compatibility**: Does it work on all supported systems?
- **Security**: Are there any security concerns?

## 🚀 Release Process

1. Version bump in relevant files
2. Update CHANGELOG.md
3. Create release notes
4. Tag release: `git tag -a v1.0.0 -m "Release 1.0.0"`
5. Push tag: `git push origin v1.0.0`
6. Create GitHub release

## ❓ Questions?

- Open a GitHub Discussion
- Open an issue with the "question" label
- Check existing issues and discussions

## 📜 License

By contributing, you agree that your contributions will be licensed under:
- MIT License for build tools and scripts
- GPL-2.0 for driver-related code (to match upstream)

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

## 🎓 Resources

### macOS Development
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Kernel Programming Guide](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/)
- [System Integrity Protection](https://developer.apple.com/documentation/security/disabling_and_enabling_system_integrity_protection)

### Swift
- [Swift.org](https://swift.org/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Swift Evolution](https://github.com/apple/swift-evolution)

### Shell Scripting
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/) - Shell script linter

### Git & GitHub
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions
- Help create a positive environment

## 🎯 Priority Areas

Current priorities for contributions:

1. **DriverKit Migration**: Modern alternative to kernel extensions
2. **Code Signing Automation**: Streamline signing process
3. **Automated Testing**: Expand test coverage
4. **macOS 16 Support**: Test and ensure compatibility
5. **Documentation**: Improve guides and troubleshooting
6. **Alternative Chipsets**: Support more Realtek chipsets

---

Thank you for contributing! 🎉

Every contribution, no matter how small, makes this project better for everyone.
