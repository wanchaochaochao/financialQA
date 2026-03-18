import axios, { AxiosError } from 'axios';
import { ChatRequest, ChatResponse, APIError } from '@/types';
import { getAuthHeader, TokenResponse } from './auth';

// Python backend URL
// 本地开发: http://localhost:9000
// 云服务器: /py-api (通过 Nginx 转发到 localhost:9000)
const PYTHON_API_URL = process.env.NEXT_PUBLIC_PYTHON_API_URL || 'http://localhost:9000';

// Create axios instance for Python backend (AI chat)
const pythonApiClient = axios.create({
  baseURL: PYTHON_API_URL,
  timeout: 60000, // 60 seconds for LLM response
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for Next.js backend (auth)
const nextApiClient = axios.create({
  baseURL: '',  // Same origin (Next.js API Routes)
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send a chat message to the AI agent (Python backend)
 */
export async function sendChatMessage(question: string): Promise<ChatResponse> {
  try {
    const request: ChatRequest = { question };
    const headers = getAuthHeader();
    const response = await pythonApiClient.post<ChatResponse>('/api/chat', request, {
      headers,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<APIError>;
      if (axiosError.response) {
        // Server responded with error
        throw new Error(axiosError.response.data.detail || 'API请求失败');
      } else if (axiosError.request) {
        // Request made but no response
        throw new Error('无法连接到AI后端服务，请确保Python FastAPI服务正在运行（端口8000）');
      }
    }
    throw new Error('发送消息时发生未知错误');
  }
}

/**
 * Check API health
 */
export async function checkAPIHealth(): Promise<boolean> {
  try {
    const response = await pythonApiClient.get('/api/health');
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

/**
 * Register a new user
 */
export async function register(
  nickname: string,
  password: string,
  phone?: string,
  email?: string
): Promise<TokenResponse> {
  try {
    const response = await nextApiClient.post<TokenResponse>('/api/auth/register', {
      nickname,
      password,
      phone,
      email,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<APIError>;
      if (axiosError.response) {
        throw new Error(axiosError.response.data.detail || '注册失败');
      }
    }
    throw new Error('注册时发生未知错误');
  }
}

/**
 * User login
 */
export async function login(
  nickname: string,
  password: string
): Promise<TokenResponse> {
  try {
    const response = await nextApiClient.post<TokenResponse>('/api/auth/login', {
      nickname,
      password,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<APIError>;
      if (axiosError.response) {
        throw new Error(axiosError.response.data.detail || '登录失败');
      }
    }
    throw new Error('登录时发生未知错误');
  }
}
