export class AgentityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AgentityError';
  }
}
