import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';

let prisma = null;

export function getPrisma() {
  // Allow hard-disable for environments where the DB is unavailable or uses an unsupported auth method.
  if (String(process.env.DISABLE_DB || '') === '1' || globalThis.__DB_DISABLED__ === true) {
    prisma = null;
    return null;
  }

  if (prisma) return prisma;

  if (!process.env.DATABASE_URL) {
    console.warn('DATABASE_URL not set — Prisma client will not be initialized');
    return null;
  }

  try {
    const connectionString = process.env.DATABASE_URL;
    const pool = new pg.Pool({ connectionString });
    pool.on('error', (err) => console.error('Postgres Pool Error:', err));
    const adapter = new PrismaPg(pool);
    prisma = new PrismaClient({ adapter });
  } catch (e) {
    console.warn('Prisma client not generated or not available:', e?.message);
    prisma = null;
  }

  return prisma;
}

export default getPrisma;
