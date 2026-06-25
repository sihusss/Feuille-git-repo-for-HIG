import { NextResponse } from 'next/server';
import { action } from '../../store';

export const runtime = 'nodejs';

export async function POST(req: Request, { params }: { params: Promise<{ code: string }> }) {
  try {
    const { code } = await params;
    const body = await req.json().catch(() => null);
    if (!isRecord(body)) throw new Error('요청 형식이 올바르지 않아.');
    if (typeof body.playerId !== 'string' || typeof body.type !== 'string') {
      throw new Error('액션 요청 정보가 부족해.');
    }
    const room = await action(code, body.playerId, body.type, body.payload);
    return NextResponse.json({ room }, { headers: { 'Cache-Control': 'no-store' } });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : '액션 실패' },
      { status: 400, headers: { 'Cache-Control': 'no-store' } }
    );
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
