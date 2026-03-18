/**
 * Get current user API
 * GET /api/auth/me
 */

import { NextRequest, NextResponse } from 'next/server';
import { getUserById } from '@/lib/server/database';
import { extractToken, verifyToken } from '@/lib/server/auth';

export async function GET(request: NextRequest) {
  try {
    // Extract token from Authorization header
    const authHeader = request.headers.get('authorization');
    const token = extractToken(authHeader);

    if (!token) {
      return NextResponse.json(
        { detail: '未提供认证令牌' },
        { status: 401 }
      );
    }

    // Verify token
    const decoded = verifyToken(token);
    if (!decoded) {
      return NextResponse.json(
        { detail: '无效或过期的令牌' },
        { status: 401 }
      );
    }

    // Get user
    const user = getUserById(decoded.sub);
    if (!user) {
      return NextResponse.json(
        { detail: '用户不存在' },
        { status: 401 }
      );
    }

    // Check if user is disabled
    if (user.status !== 1) {
      return NextResponse.json(
        { detail: '用户已被禁用' },
        { status: 403 }
      );
    }

    // Return user info
    return NextResponse.json({
      id: user.id,
      nickname: user.nickname,
      phone: user.phone,
      email: user.email,
      vip_level: user.vip_level,
      vip_expire: user.vip_expire,
      status: user.status === 1,
      created_at: user.created_at,
      last_login: user.last_login,
    });
  } catch (error) {
    console.error('Get user error:', error);
    return NextResponse.json(
      { detail: '获取用户信息失败' },
      { status: 500 }
    );
  }
}
