import { NextResponse } from 'next/server';
import { createRoom } from './store';

export const runtime = 'nodejs';

export async function POST(req: Request) {
  try {
    await req.json().catch(() => ({}));
    return NextResponse.json(await createRoom(), { headers: { 'Cache-Control': 'no-store' } });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : '방 생성 실패' },
      { status: 400, headers: { 'Cache-Control': 'no-store' } }
    );
  }
}
