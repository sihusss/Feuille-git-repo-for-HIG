import { NextResponse } from 'next/server';
import { publicRoom } from '../store';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(req: Request, { params }: { params: Promise<{ code: string }> }) {
  try {
    const { code } = await params;
    const { searchParams } = new URL(req.url);
    const result = await publicRoom(code, searchParams.get('playerId'), req.headers.get('if-none-match'));
    const headers = responseHeaders(result.etag);

    if (result.notModified) {
      return new Response(null, { status: 304, headers });
    }

    if (!result.room) {
      return NextResponse.json(
        { error: '방을 찾을 수 없어.' },
        { status: 404, headers }
      );
    }

    return NextResponse.json({ room: result.room }, { headers });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : '방을 불러오지 못했어.' },
      { status: 500, headers: responseHeaders() }
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
