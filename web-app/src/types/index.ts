// Message types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// API Request/Response types
export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  question: string;
  answer: string;
  timestamp: string;
  model: string;
}

// API Error type
export interface APIError {
  detail: string;
}
