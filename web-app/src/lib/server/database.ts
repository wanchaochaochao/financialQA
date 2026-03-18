/**
 * Database utilities for Next.js backend
 * Using better-sqlite3 for SQLite database
 */

import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

// Database file path
const dbDir = path.join(process.cwd(), '..', 'data');
const dbPath = path.join(dbDir, 'financial_qa.db');

// Ensure data directory exists
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

// Create database connection
export const db = new Database(dbPath);

// Enable WAL mode for better performance
db.pragma('journal_mode = WAL');

/**
 * Initialize database tables
 */
export function initDatabase() {
  const createUsersTable = `
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nickname TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      phone TEXT UNIQUE,
      email TEXT UNIQUE,
      vip_level INTEGER DEFAULT 0,
      vip_expire TEXT,
      status INTEGER DEFAULT 1,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      last_login TEXT
    )
  `;

  db.exec(createUsersTable);

  // Create indexes
  db.exec('CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname)');
  db.exec('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)');
  db.exec('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)');
}

// Initialize database on module load
initDatabase();

/**
 * User type
 */
export interface User {
  id: number;
  nickname: string;
  password_hash: string;
  phone: string | null;
  email: string | null;
  vip_level: number;
  vip_expire: string | null;
  status: number;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

/**
 * Get user by nickname
 */
export function getUserByNickname(nickname: string): User | undefined {
  const stmt = db.prepare('SELECT * FROM users WHERE nickname = ?');
  return stmt.get(nickname) as User | undefined;
}

/**
 * Get user by ID
 */
export function getUserById(id: number): User | undefined {
  const stmt = db.prepare('SELECT * FROM users WHERE id = ?');
  return stmt.get(id) as User | undefined;
}

/**
 * Get user by phone
 */
export function getUserByPhone(phone: string): User | undefined {
  const stmt = db.prepare('SELECT * FROM users WHERE phone = ?');
  return stmt.get(phone) as User | undefined;
}

/**
 * Get user by email
 */
export function getUserByEmail(email: string): User | undefined {
  const stmt = db.prepare('SELECT * FROM users WHERE email = ?');
  return stmt.get(email) as User | undefined;
}

/**
 * Create a new user
 */
export function createUser(
  nickname: string,
  passwordHash: string,
  phone?: string,
  email?: string
): User {
  const stmt = db.prepare(`
    INSERT INTO users (nickname, password_hash, phone, email)
    VALUES (?, ?, ?, ?)
  `);

  const result = stmt.run(nickname, passwordHash, phone || null, email || null);

  return getUserById(result.lastInsertRowid as number)!;
}

/**
 * Update user's last login time
 */
export function updateLastLogin(userId: number): void {
  const stmt = db.prepare(`
    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
  `);
  stmt.run(userId);
}

/**
 * Check if user's VIP is active
 */
export function isVipActive(user: User): boolean {
  if (user.vip_level === 0) return false;
  if (!user.vip_expire) return false;

  const expireDate = new Date(user.vip_expire);
  return expireDate > new Date();
}
