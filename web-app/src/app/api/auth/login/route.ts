/**
 * User login API
 * POST /api/auth/login
 */

import { NextRequest, NextResponse } from 'next/server';
import { getUserByNickname, updateLastLogin, isVipActive } from '@/lib/server/database';
import { verifyPassword, createToken } from '@/lib/server/auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { nickname, password } = body;

    // Validation
    if (!nickname || typeof nickname !== 'string') {
      return NextResponse.json(
        { detail: '用户名不能为空' },
        { status: 400 }
      );
    }

    if (!password || typeof password !== 'string') {
      return NextResponse.json(
        { detail: '密码不能为空' },
        { status: 400 }
      );
    }

    // Get user
    const user = getUserByNickname(nickname);
    if (!user) {
      return NextResponse.json(
        { detail: '用户名或密码错误' },
        { status: 401 }
      );
    }

    // Verify password
    const isPasswordValid = await verifyPassword(password, user.password_hash);
    if (!isPasswordValid) {
      return NextResponse.json(
        { detail: '用户名或密码错误' },
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

    // Update last login
    updateLastLogin(user.id);

    // Create token
    const accessToken = createToken(user.id);

    // Return response
    return NextResponse.json({
      access_token: accessToken,
      token_type: 'bearer',
      user: {
        id: user.id,
        nickname: user.nickname,
        phone: user.phone,
        email: user.email,
        vip_level: user.vip_level,
        vip_active: isVipActive(user),
        status: user.status === 1,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { detail: '登录失败，请稍后重试' },
      { status: 500 }
    );
  }
}
