// Mirrors docs/API.md's User object and error envelope exactly.

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string | null;
}

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}
