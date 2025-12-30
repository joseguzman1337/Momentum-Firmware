const fs = require('fs').promises;
const path = require('path');

class ImportProcessor {
  constructor() {
    this.maxDepth = 5;
    this.importStack = new Set();
  }

  async processImports(content, basePath, debugMode = false) {
    const importTree = { path: basePath, imports: [] };
    const processed = await this._processContent(content, basePath, 0, importTree, debugMode);
    return { content: processed, importTree };
  }

  async _processContent(content, basePath, depth, tree, debug) {
    if (depth >= this.maxDepth) {
      if (debug) console.log(`Max depth ${this.maxDepth} reached`);
      return content;
    }

    const importRegex = /^@(\.?\/[^\s]+\.md)$/gm;
    let result = content;
    let match;

    while ((match = importRegex.exec(content)) !== null) {
      const importPath = match[1];
      const resolvedPath = path.resolve(basePath, importPath);
      
      if (this.importStack.has(resolvedPath)) {
        if (debug) console.log(`Circular import detected: ${resolvedPath}`);
        result = result.replace(match[0], `<!-- Circular import prevented: ${importPath} -->`);
        continue;
      }

      try {
        this.importStack.add(resolvedPath);
        const importContent = await fs.readFile(resolvedPath, 'utf8');
        const importBasePath = path.dirname(resolvedPath);
        
        const childTree = { path: resolvedPath, imports: [] };
        tree.imports.push(childTree);
        
        const processedImport = await this._processContent(importContent, importBasePath, depth + 1, childTree, debug);
        result = result.replace(match[0], processedImport);
        
        this.importStack.delete(resolvedPath);
      } catch (error) {
        if (debug) console.log(`Import failed: ${importPath} - ${error.message}`);
        result = result.replace(match[0], `<!-- Import failed: ${importPath} -->`);
      }
    }

    return result;
  }

  validateImportPath(importPath, basePath, allowedDirs = []) {
    const resolved = path.resolve(basePath, importPath);
    return allowedDirs.length === 0 || allowedDirs.some(dir => resolved.startsWith(path.resolve(dir)));
  }

  async findProjectRoot(startDir) {
    let current = startDir;
    while (current !== path.dirname(current)) {
      try {
        await fs.access(path.join(current, '.git'));
        return current;
      } catch {
        current = path.dirname(current);
      }
    }
    return startDir;
  }
}

module.exports = { ImportProcessor };