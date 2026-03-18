'use client';

import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function InputBox({ onSend, disabled = false }: InputBoxProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t px-4 py-4 backdrop-blur-sm" style={{
      background: 'var(--bg-elevated)',
      borderColor: 'var(--border-default)'
    }}>
      <div className="flex gap-2 items-end">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="请输入您的问题... (按 Enter 发送, Shift+Enter 换行)"
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none rounded-lg px-4 py-3 focus:outline-none disabled:cursor-not-allowed min-h-[52px] max-h-[200px] transition-all"
          style={{
            height: 'auto',
            minHeight: '52px',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-blue)'}
          onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-default)'}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || disabled}
          className="flex-shrink-0 text-white rounded-lg px-4 py-3 disabled:cursor-not-allowed transition-all flex items-center gap-2 h-[52px]"
          style={{
            background: disabled || !input.trim() ? 'var(--border-light)' : 'var(--accent-blue)',
            boxShadow: (!disabled && input.trim()) ? '0 2px 8px rgba(10, 126, 164, 0.3)' : 'none'
          }}
          onMouseEnter={(e) => {
            if (!disabled && input.trim()) {
              e.currentTarget.style.background = '#0d95bb';
            }
          }}
          onMouseLeave={(e) => {
            if (!disabled && input.trim()) {
              e.currentTarget.style.background = 'var(--accent-blue)';
            }
          }}
        >
          <Send className="w-4 h-4" />
          <span className="font-medium">发送</span>
        </button>
      </div>
    </div>
  );
}
