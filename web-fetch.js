const https = require('https');
const http = require('http');
const { URL } = require('url');

class WebFetch {
  constructor() {
    this.maxUrls = 20;
  }

  async webFetch(prompt) {
    const urls = this.extractUrls(prompt);
    
    if (urls.length === 0) {
      throw new Error('No valid URLs found in prompt. URLs must start with http:// or https://');
    }

    if (urls.length > this.maxUrls) {
      throw new Error(`Too many URLs (${urls.length}). Maximum allowed: ${this.maxUrls}`);
    }

    console.log(`Found ${urls.length} URL(s). Fetching content...`);
    
    const contents = await Promise.all(
      urls.map(async (url, index) => {
        try {
          const content = await this.fetchUrl(url);
          return { url, content, index };
        } catch (error) {
          return { url, error: error.message, index };
        }
      })
    );

    return this.formatResponse(prompt, contents);
  }

  extractUrls(text) {
    const urlRegex = /https?:\/\/[^\s<>"{}|\\^`[\]]+/g;
    return [...new Set(text.match(urlRegex) || [])];
  }

  async fetchUrl(url) {
    return new Promise((resolve, reject) => {
      const parsedUrl = new URL(url);
      const client = parsedUrl.protocol === 'https:' ? https : http;
      
      const options = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port,
        path: parsedUrl.pathname + parsedUrl.search,
        method: 'GET',
        headers: {
          'User-Agent': 'Gemini-CLI-WebFetch/1.0'
        },
        timeout: 10000
      };

      const req = client.request(options, (res) => {
        let data = '';
        
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(this.extractTextContent(data));
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      req.end();
    });
  }

  extractTextContent(html) {
    return html
      .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
      .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .substring(0, 8000); // Limit content length
  }

  formatResponse(prompt, contents) {
    let response = `Processing prompt: "${prompt}"\n\n`;
    
    contents.forEach(({ url, content, error, index }) => {
      response += `## Source ${index + 1}: ${url}\n`;
      if (error) {
        response += `Error: ${error}\n\n`;
      } else {
        response += `Content: ${content.substring(0, 1000)}${content.length > 1000 ? '...' : ''}\n\n`;
      }
    });

    return response;
  }
}

module.exports = { WebFetch };