/**
 * User registration API
 * POST /api/auth/register
 */

import { NextRequest, NextResponse } from 'next/server';
import {
  createUser,
  getUserByNickname,
  getUserByPhone,
  getUserByEmail,
  updateLastLogin,
} from '@/lib/server/database';
import { hashPassword, createToken } from '@/lib/server/auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { nickname, password, phone, email } = body;

    // Validation
    if (!nickname || typeof nickname !== 'string') {
      return NextResponse.json(
        { detail: '用户名不能为空' },
        { status: 400 }
      );
    }

    if (nickname.length < 3) {
      return NextResponse.json(
        { detail: '用户名至少3个字符' },
        { status: 400 }
      );
    }

    if (!password || typeof password !== 'string') {
      return NextResponse.json(
        { detail: '密码不能为空' },
        { status: 400 }
      );
    }

    if (password.length < 6) {
      return NextResponse.json(
        { detail: '密码至少6个字符' },
        { status: 400 }
      );
    }

    // Check if nickname exists
    const existingUser = getUserByNickname(nickname);
    if (existingUser) {
      return NextResponse.json(
        { detail: '用户名已存在' },
        { status: 400 }
      );
    }

    // Check if phone exists (if provided)
    if (phone) {
      const existingPhone = getUserByPhone(phone);
      if (existingPhone) {
        return NextResponse.json(
          { detail: '手机号已被注册' },
          { status: 400 }
        );
      }
    }

    // Check if email exists (if provided)
    if (email) {
      const existingEmail = getUserByEmail(email);
      if (existingEmail) {
        return NextResponse.json(
          { detail: '邮箱已被注册' },
          { status: 400 }
        );
      }
    }

    // Hash password
    const passwordHash = await hashPassword(password);

    // Create user
    const user = createUser(nickname, passwordHash, phone, email);

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
        status: user.status === 1,
      },
    });
  } catch (error) {
    console.error('Register error:', error);
    return NextResponse.json(
      { detail: '注册失败，请稍后重试' },
      { status: 500 }
    );
  }
}
