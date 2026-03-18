'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Message } from '@/types';
import { sendChatMessage } from '@/lib/api';
import { generateId } from '@/lib/utils';
import { isAuthenticated, getUser, clearAuth, User } from '@/lib/auth';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { ExampleQuestions } from './ExampleQuestions';
import { AlertCircle, LogOut, User as UserIcon } from 'lucide-react';

export function ChatInterface() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      if (!isAuthenticated()) {
        router.push('/login');
      } else {
        const currentUser = getUser();
        setUser(currentUser);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    clearAuth();
    router.push('/login');
  };

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Call API
      const response = await sendChatMessage(content);

      // Add assistant message
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(response.timestamp),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : '发生未知错误');

      // Add error message
      const errorMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: `抱歉，处理您的问题时出现错误：\n\n${err instanceof Error ? err.message : '未知错误'}\n\n请确保 Python FastAPI 后端服务正在运行（端口8000）。`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* Header - Dark Financial Style */}
      <header className="border-b px-6 py-4 backdrop-blur-sm" style={{
        background: 'var(--bg-elevated)',
        borderColor: 'var(--border-default)'
      }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              金融资产问答系统
            </h1>
            <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
              基于 AI 的智能金融数据分析与知识问答平台
            </p>
          </div>
          <div className="flex items-center gap-3">
            {user && (
              <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                <UserIcon className="w-4 h-4" />
                <span>{user.nickname}</span>
                {user.vip_level > 0 && (
                  <span className="px-2 py-0.5 rounded text-xs font-medium" style={{
                    background: 'var(--accent-gold)',
                    color: 'var(--bg-primary)'
                  }}>
                    VIP{user.vip_level}
                  </span>
                )}
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-md transition-all"
              style={{
                color: 'var(--text-secondary)',
                background: 'transparent'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              title="退出登录"
            >
              <LogOut className="w-4 h-4" />
              退出
            </button>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium" style={{
              background: 'var(--accent-teal)',
              color: 'white'
            }}>
              <span className="w-2 h-2 rounded-full mr-2" style={{
                background: '#10b981'
              }}></span>
              运行中
            </span>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="border-b px-6 py-3" style={{
          background: 'rgba(220, 38, 38, 0.1)',
          borderColor: 'rgba(220, 38, 38, 0.2)'
        }}>
          <div className="flex items-center gap-2" style={{ color: '#fca5a5' }}>
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-medium">{error}</span>
          </div>
        </div>
      )}

      {/* Example Questions */}
      {messages.length === 0 && (
        <ExampleQuestions
          onSelectQuestion={handleSendMessage}
          disabled={isLoading}
        />
      )}

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <InputBox onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
