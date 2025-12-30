# Go Development Tools - Installed Versions

**Last Updated**: 2025-12-22 23:03

## Installed Tools

| Tool | Version | Purpose | Repository |
|------|---------|---------|------------|
| **gopls** | v0.21.0 | Go language server for IDE integration | [golang.org/x/tools/gopls](https://pkg.go.dev/golang.org/x/tools/gopls) |
| **golangci-lint** | v1.64.8 | Meta-linter (50+ linters) | [github.com/golangci/golangci-lint](https://github.com/golangci/golangci-lint) |
| **delve (dlv)** | v1.26.0 | Interactive Go debugger | [github.com/go-delve/delve](https://github.com/go-delve/delve) |
| **goimports** | v0.21.0 | Auto-format + import management | [golang.org/x/tools/cmd/goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports) |
| **godoc** | v0.21.0 | Documentation server/viewer | [golang.org/x/tools/cmd/godoc](https://pkg.go.dev/golang.org/x/tools/cmd/godoc) |

## System Information

- **Go Version**: go1.25.1 darwin/arm64
- **GOPATH**: /Users/x/go
- **GOBIN**: /Users/x/go/bin
- **Installation Location**: /Users/x/go/bin/

## Version Check Commands

```bash
# Check all tool versions
/Users/x/go/bin/gopls version
/Users/x/go/bin/golangci-lint version
/Users/x/go/bin/dlv version
go version
```

## Upgrade Instructions

To upgrade all tools to the latest versions:

```bash
./scripts/setup-go-tools.sh
```

The script will:
1. Force reinstall all tools with `@latest` tag
2. Verify installations
3. Show current versions
4. Update this file's timestamp

## Integration Status

### VS Code
✅ Configured in [.vscode/settings.json](../.vscode/settings.json):
```json
{
  "go.alternateTools": {
    "gopls": "/Users/x/go/bin/gopls"
  },
  "go.useLanguageServer": true
}
```

### IDE Features Enabled
- ✅ Autocomplete and IntelliSense
- ✅ Go to definition/references
- ✅ Code formatting (goimports)
- ✅ Linting (golangci-lint)
- ✅ Debugging (delve)
- ✅ Documentation on hover
- ✅ Rename refactoring

## Troubleshooting

### gopls not working in VS Code
1. Reload VS Code: `Cmd+Shift+P` → "Developer: Reload Window"
2. Check output panel: View → Output → Select "Go"
3. Verify path: Settings → search "gopls" → check alternate tools

### Tools not found in terminal
Add GOBIN to PATH in `~/.zshrc` or `~/.bashrc`:
```bash
export PATH="$PATH:/Users/x/go/bin"
```

### Check for updates
```bash
# Check latest gopls version
go list -m -versions golang.org/x/tools/gopls

# Check latest golangci-lint
curl -s https://api.github.com/repos/golangci/golangci-lint/releases/latest | grep tag_name

# Check latest delve
curl -s https://api.github.com/repos/go-delve/delve/releases/latest | grep tag_name
```

## CI/CD Integration

These tools are for **local development only**. CI/CD should install tools independently:

```yaml
# .github/workflows/go.yml
- name: Install Go tools
  run: |
    go install golang.org/x/tools/gopls@v0.21.0
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.64.8
```

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Repository documentation
- [scripts/README.md](README.md) - Setup scripts guide
- [Go Modules](..//src/base/go.mod) - Primary Go module
- [SS7 Core](..//src/ai/knowledge/satellite/ss7/core/go.mod) - Secondary Go module
