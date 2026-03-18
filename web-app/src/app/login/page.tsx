'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { login } from '@/lib/api';
import { saveAuth } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [nickname, setNickname] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!nickname.trim()) {
      setError('请输入用户名');
      return;
    }

    if (!password) {
      setError('请输入密码');
      return;
    }

    setLoading(true);

    try {
      const response = await login(nickname, password);
      saveAuth(response);
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'var(--bg-primary)' }}>
      <div className="max-w-md w-full space-y-8 p-8 rounded-xl" style={{
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border-default)',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.5)'
      }}>
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold" style={{ color: 'var(--text-primary)' }}>
            登录账号
          </h2>
          <p className="mt-2 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
            还没有账号？{' '}
            <Link href="/register" className="font-medium" style={{ color: 'var(--accent-blue)' }}>
              立即注册
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md p-4" style={{
              background: 'rgba(220, 38, 38, 0.1)',
              border: '1px solid rgba(220, 38, 38, 0.2)'
            }}>
              <p className="text-sm" style={{ color: '#fca5a5' }}>{error}</p>
            </div>
          )}

          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="nickname" className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                用户名
              </label>
              <input
                id="nickname"
                name="nickname"
                type="text"
                required
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 rounded-md focus:outline-none sm:text-sm"
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-default)',
                  color: 'var(--text-primary)',
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-blue)'}
                onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-default)'}
                placeholder="请输入用户名"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                密码
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 rounded-md focus:outline-none sm:text-sm"
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-default)',
                  color: 'var(--text-primary)',
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = 'var(--accent-blue)'}
                onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-default)'}
                placeholder="请输入密码"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              style={{
                background: loading ? 'var(--border-light)' : 'var(--accent-blue)',
                boxShadow: !loading ? '0 2px 8px rgba(10, 126, 164, 0.3)' : 'none'
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.currentTarget.style.background = '#0d95bb';
                }
              }}
              onMouseLeave={(e) => {
                if (!loading) {
                  e.currentTarget.style.background = 'var(--accent-blue)';
                }
              }}
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </div>
        </form>

        <div className="text-center mt-4">
          <Link
            href="/"
            className="text-sm transition-colors"
            style={{ color: 'var(--text-secondary)' }}
            onMouseEnter={(e) => e.currentTarget.style.color = 'var(--text-primary)'}
            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}
          >
            ← 返回首页
          </Link>
        </div>
      </div>
    </div>
  );
}
