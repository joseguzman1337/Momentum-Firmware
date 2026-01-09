import { Codex } from '@openai/codex-sdk';

export class CodexSDKIntegration {
  private codex: Codex;
  
  constructor() {
    this.codex = new Codex();
  }

  async processComplexTask(task: string, threadId?: string): Promise<string> {
    const thread = threadId ? this.codex.resumeThread(threadId) : this.codex.startThread();
    const result = await thread.run(task);
    return result;
  }

  async generateStructuredOutput(task: string, schema: object): Promise<any> {
    const thread = this.codex.startThread();
    const result = await thread.run(task, { outputSchema: schema });
    return JSON.parse(result);
  }
}

// Export for use in CI/CD pipelines
export const codexSDK = new CodexSDKIntegration();