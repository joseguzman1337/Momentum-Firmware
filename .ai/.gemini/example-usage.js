const { ImportProcessor } = require('./memory-import-processor');

async function example() {
  const processor = new ImportProcessor();
  
  // Example GEMINI.md content with imports
  const content = `# Main Document

This is the main content.

@./components/instructions.md

More content here.

@./shared/config.md`;

  try {
    const result = await processor.processImports(content, __dirname, true);
    console.log('Processed Content:');
    console.log(result.content);
    console.log('\nImport Tree:');
    console.log(JSON.stringify(result.importTree, null, 2));
  } catch (error) {
    console.error('Processing failed:', error.message);
  }
}

// Run example if this file is executed directly
if (require.main === module) {
  example();
}

module.exports = { example };