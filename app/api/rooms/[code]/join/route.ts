import { NextResponse } from 'next/server';
import { joinRoom } from '../../store';

export const runtime = 'nodejs';

export async function POST(req: Request, { params }: { params: Promise<{ code: string }> }) {
  try {
    const { code } = await params;
    await req.json().catch(() => ({}));
    return NextResponse.json(await joinRoom(code), { headers: { 'Cache-Control': 'no-store' } });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : '입장 실패' },
      { status: 400, headers: { 'Cache-Control': 'no-store' } }
    );
  }
}
