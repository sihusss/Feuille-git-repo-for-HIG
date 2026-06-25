import { NextResponse } from 'next/server';
import { etagForRoom, joinRoom } from '../../store';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request, { params }: { params: Promise<{ code: string }> }) {
  try {
    const { code } = await params;
    await req.json().catch(() => ({}));
    const result = await joinRoom(code);
    return NextResponse.json(result, { headers: responseHeaders(etagForRoom(result.room)) });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : '입장 실패' },
      { status: 400, headers: responseHeaders() }
    );
  }
}

function responseHeaders(etag?: string) {
  const headers = new Headers({
    'Cache-Control': 'private, no-store, max-age=0',
    'X-Content-Type-Options': 'nosniff'
  });
  if (etag) headers.set('ETag', etag);
  return headers;
}
