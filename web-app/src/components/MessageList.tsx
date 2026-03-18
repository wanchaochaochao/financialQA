'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/types';
import { MessageItem } from './MessageItem';
import { Loader2 } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full" style={{ color: 'var(--text-secondary)' }}>
          <p className="text-lg font-medium mb-2">欢迎使用金融资产问答系统</p>
          <p className="text-sm">请输入您的问题或点击下方示例问题开始</p>
        </div>
      )}

      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="flex gap-3 justify-start">
          <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style={{
            background: 'var(--accent-blue)',
            boxShadow: '0 0 0 3px rgba(10, 126, 164, 0.1)'
          }}>
            <Loader2 className="w-5 h-5 text-white animate-spin" />
          </div>
          <div className="rounded-lg px-4 py-3" style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)'
          }}>
            <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">AI 正在思考...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
