#!/usr/bin/env node

const { WebFetch } = require('./web-fetch');

async function main() {
  const webFetch = new WebFetch();
  
  // Get prompt from command line arguments
  const prompt = process.argv.slice(2).join(' ');
  
  if (!prompt) {
    console.log('Usage: node web-fetch-cli.js "Your prompt with URLs like https://example.com"');
    console.log('\nExamples:');
    console.log('  node web-fetch-cli.js "Summarize https://example.com/article"');
    console.log('  node web-fetch-cli.js "Compare https://site1.com and https://site2.com"');
    process.exit(1);
  }

  try {
    const result = await webFetch.webFetch(prompt);
    console.log(result);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Example usage function
async function examples() {
  const webFetch = new WebFetch();
  
  console.log('=== Web Fetch Examples ===\n');
  
  // Example 1: Single URL
  try {
    console.log('Example 1: Single URL summary');
    const result1 = await webFetch.webFetch('Summarize the main points of https://httpbin.org/json');
    console.log(result1);
  } catch (error) {
    console.log('Example 1 failed:', error.message);
  }
  
  console.log('\n' + '='.repeat(50) + '\n');
  
  // Example 2: Multiple URLs
  try {
    console.log('Example 2: Multiple URL comparison');
    const result2 = await webFetch.webFetch('Compare https://httpbin.org/json and https://httpbin.org/xml');
    console.log(result2);
  } catch (error) {
    console.log('Example 2 failed:', error.message);
  }
}

// Run main if called directly, or examples if --examples flag
if (require.main === module) {
  if (process.argv.includes('--examples')) {
    examples();
  } else {
    main();
  }
}

module.exports = { main, examples };