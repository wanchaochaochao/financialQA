'use client';

import { Lightbulb } from 'lucide-react';

interface ExampleQuestionsProps {
  onSelectQuestion: (question: string) => void;
  disabled?: boolean;
}

const EXAMPLE_QUESTIONS = [
  '阿里巴巴现在的股价是多少？',
  '特斯拉最近7天涨跌情况如何？',
  '什么是市盈率？',
  '贵州茅台最近30天走势如何？',
  '收入和净利润的区别是什么？',
  '上证指数的最新行情如何？',
];

export function ExampleQuestions({ onSelectQuestion, disabled = false }: ExampleQuestionsProps) {
  return (
    <div className="border-b px-4 py-4" style={{
      background: 'var(--bg-secondary)',
      borderColor: 'var(--border-default)'
    }}>
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-4 h-4" style={{ color: 'var(--accent-blue)' }} />
        <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>示例问题（点击快速提问）</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((question, index) => (
          <button
            key={index}
            onClick={() => !disabled && onSelectQuestion(question)}
            disabled={disabled}
            className="rounded-lg px-3 py-2 text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-default)',
              color: 'var(--text-secondary)',
            }}
            onMouseEnter={(e) => {
              if (!disabled) {
                e.currentTarget.style.background = 'var(--bg-hover)';
                e.currentTarget.style.borderColor = 'var(--accent-blue)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }
            }}
            onMouseLeave={(e) => {
              if (!disabled) {
                e.currentTarget.style.background = 'var(--bg-tertiary)';
                e.currentTarget.style.borderColor = 'var(--border-default)';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }
            }}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
