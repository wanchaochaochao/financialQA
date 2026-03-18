'use client';

import { Message } from '@/types';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style={{
          background: 'var(--accent-blue)',
          boxShadow: '0 0 0 3px rgba(10, 126, 164, 0.1)'
        }}>
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}

      <div
        className="max-w-[80%] rounded-lg px-4 py-3"
        style={isUser ? {
          background: 'var(--accent-blue)',
          color: 'white',
          boxShadow: '0 2px 8px rgba(10, 126, 164, 0.2)'
        } : {
          background: 'var(--bg-elevated)',
          color: 'var(--text-primary)',
          border: '1px solid var(--border-default)',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)'
        }}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none prose-headings:text-gray-200 prose-p:text-gray-300 prose-strong:text-gray-100 prose-code:text-teal-300 prose-code:bg-gray-800 prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-img:rounded-lg prose-img:shadow-md prose-img:max-w-full prose-img:h-auto prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
        <div className="text-xs mt-2" style={{
          color: isUser ? 'rgba(255, 255, 255, 0.7)' : 'var(--text-tertiary)'
        }}>
          {message.timestamp.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style={{
          background: 'var(--accent-gold)',
          boxShadow: '0 0 0 3px rgba(201, 168, 96, 0.1)'
        }}>
          <User className="w-5 h-5" style={{ color: 'var(--bg-primary)' }} />
        </div>
      )}
    </div>
  );
}
