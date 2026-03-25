# Momentum Firmware - Development Guidelines

## Code Quality Standards

### Naming Conventions
- **Functions**: Snake case with module prefix (e.g., `furi_hal_power_init`, `storage_file_init`)
- **Types**: Pascal case with module prefix (e.g., `StorageFile`, `JsGpioPinInst`, `CanvasOrientation`)
- **Constants**: Upper snake case with module prefix (e.g., `FURI_HAL_POWER_CHARGE_CURRENT_LIMIT_DEFAULT_MA`)
- **Enums**: Pascal case enum name, upper case values (e.g., `ColorWhite`, `FontPrimary`)
- **Macros**: Upper snake case (e.g., `TAG`, `INTERRUPT_QUEUE_LEN`)

### File Organization Patterns
- **Header guards**: `#pragma once` preferred over traditional guards
- **Include order**: System headers, then local headers, separated by blank lines
- **Module structure**: Private types and functions at top, public API at bottom
- **Tag definition**: `#define TAG "ModuleName"` for logging consistency

### Documentation Standards
- **Doxygen comments**: Use `/** */` for public API documentation
- **Function documentation**: Include `@param` and `@return` tags
- **Example usage**: Provide JavaScript examples for JS modules
- **Brief descriptions**: Start with `@brief` for function summaries

## Architectural Patterns

### Memory Management
- **RTOS integration**: Use Furi abstractions over direct FreeRTOS calls
- **Dynamic allocation**: Always check allocation success with `furi_check()`
- **Resource cleanup**: Implement proper cleanup in destroy functions
- **Critical sections**: Use `FURI_CRITICAL_ENTER()/EXIT()` for atomic operations

### Error Handling
- **Assertion usage**: `furi_assert()` for runtime checks, `furi_check()` for critical failures
- **Return codes**: Use enum-based status codes (e.g., `StorageStatus`)
- **Null checks**: Always validate pointers before use
- **Graceful degradation**: Provide fallback values when hardware unavailable

### Hardware Abstraction
- **HAL layer**: All hardware access through `furi_hal_*` functions
- **Resource acquisition**: Use acquire/release pattern for shared resources
- **GPIO management**: Initialize pins with proper mode, pull, and speed settings
- **I2C communication**: Always acquire/release I2C handles around transactions

## JavaScript Integration Patterns

### Module Structure
- **Plugin descriptor**: Use standard `FlipperAppPluginDescriptor` structure
- **Context management**: Store module state in context structures
- **Resource cleanup**: Implement proper destroy functions for JS modules
- **Event loop integration**: Use Furi event loop for asynchronous operations

### API Design
- **Value parsing**: Use `JS_VALUE_PARSE_ARGS_OR_RETURN` for argument validation
- **Enum definitions**: Define JavaScript-friendly enums with string variants
- **Object creation**: Use `JS_ASSIGN_MULTI` for clean object field assignment
- **Error handling**: Use `JS_ERROR_AND_RETURN` for JavaScript exceptions

### Memory Management in JS
- **Foreign objects**: Use `mjs_mk_foreign()` for native object wrapping
- **Semaphores**: Create semaphores for interrupt handling
- **Array management**: Use mlib arrays for dynamic collections
- **Contract objects**: Implement event loop contracts for async operations

## Build System Conventions

### Configuration Management
- **Options file**: Use `fbt_options.py` for build configuration
- **Environment variables**: Support environment overrides for CI/CD
- **Version handling**: Automatic version detection from git tags
- **Conditional compilation**: Use feature flags for optional components

### Target Configuration
- **Hardware targets**: Support multiple hardware revisions (f7, f18)
- **Optimization flags**: Separate debug and release optimization settings
- **Toolchain versions**: Specify supported compiler versions
- **External dependencies**: Manage submodules and external libraries

## Service Architecture Patterns

### Service Registration
- **Record system**: Use Furi record system for service discovery
- **Initialization order**: Services initialize in dependency order
- **Singleton pattern**: Most services are singletons accessed via records
- **Thread management**: Each service typically runs in its own thread

### Inter-Service Communication
- **Message queues**: Use Furi message queues for async communication
- **Event loops**: Integrate with Furi event loop for event-driven architecture
- **Pub/sub pattern**: Use notification service for broadcast events
- **Callback registration**: Support callback-based event notification

### Storage Service Patterns
- **File management**: Track open files with unique identifiers
- **Path validation**: Always validate file paths before operations
- **Status reporting**: Provide detailed status information for debugging
- **Concurrent access**: Handle multiple file operations safely

## Testing and Quality Assurance

### Unit Testing
- **Test organization**: Group tests by module functionality
- **Mock objects**: Use mocks for hardware abstraction layer testing
- **Assertion patterns**: Use descriptive assertions with clear failure messages
- **Coverage targets**: Aim for high coverage of critical code paths

### Static Analysis
- **PVS-Studio**: Regular static analysis with PVS-Studio
- **Clang tools**: Use clang-format and clang-tidy for code quality
- **Warning levels**: Compile with high warning levels and treat warnings as errors
- **Code review**: Mandatory code review for all changes

### Performance Considerations
- **Memory usage**: Monitor stack and heap usage carefully
- **Real-time constraints**: Ensure interrupt handlers are fast and non-blocking
- **Power management**: Implement proper sleep/wake cycles
- **Resource limits**: Respect hardware limitations (RAM, flash, CPU)

## AI Development Integration

### Automated Code Generation
- **Pattern recognition**: AI agents learn from existing code patterns
- **Style consistency**: Maintain consistent coding style across AI-generated code
- **Documentation generation**: Auto-generate documentation for new functions
- **Test generation**: Create unit tests for new functionality

### Quality Assurance
- **Automated review**: AI agents perform initial code review
- **Security scanning**: Continuous security vulnerability detection
- **Performance analysis**: Automated performance regression detection
- **Compatibility testing**: Ensure changes don't break existing functionality

### Development Workflow
- **Issue processing**: AI agents automatically process GitHub issues
- **PR generation**: Automated pull request creation and management
- **Continuous integration**: AI-powered CI/CD pipeline management
- **Knowledge sharing**: RAG system for development knowledge base