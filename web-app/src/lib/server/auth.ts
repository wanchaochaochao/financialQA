/**
 * Authentication utilities for Next.js backend
 */

import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

// JWT secret key
const JWT_SECRET = process.env.JWT_SECRET_KEY || 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = '7d'; // 7 days

/**
 * Hash a password
 */
export async function hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

/**
 * Verify password against hash
 */
export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

/**
 * Create JWT token
 */
export function createToken(userId: number): string {
  return jwt.sign({ sub: userId }, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
  });
}

/**
 * Verify and decode JWT token
 */
export function verifyToken(token: string): { sub: number } | null {
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as { sub: number };
    return decoded;
  } catch (error) {
    return null;
  }
}

/**
 * Extract token from Authorization header
 */
export function extractToken(authHeader: string | null): string | null {
  if (!authHeader) return null;

  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') {
    return null;
  }

  return parts[1];
}
