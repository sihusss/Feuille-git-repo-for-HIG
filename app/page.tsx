'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);
  const normalizedCode = code.replace(/\D/g, '').slice(0, 6);

  async function createRoom() {
    if (pending) return;
    setError('');
    setPending(true);

    try {
      const res = await fetch('/api/rooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await readJson(res);
      if (!res.ok) {
        setError(errorMessage(data, '방 생성 실패'));
        return;
      }
      if (!isRecord(data.room) || typeof data.room.code !== 'string' || typeof data.playerId !== 'string') {
        setError('서버 응답 형식이 올바르지 않습니다.');
        return;
      }
      rememberPlayerId(data.room.code, data.playerId);
      router.push(`/room/${data.room.code}`);
    } catch {
      setError('네트워크 연결을 확인해주세요.');
    } finally {
      setPending(false);
    }
  }

  async function joinRoom(e: FormEvent) {
    e.preventDefault();
    if (pending) return;
    if (normalizedCode.length !== 6) {
      setError('6자리 참가 코드를 입력해주세요.');
      return;
    }

    setError('');
    setPending(true);

    try {
      const res = await fetch(`/api/rooms/${normalizedCode}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await readJson(res);
      if (!res.ok) {
        setError(errorMessage(data, '입장 실패'));
        return;
      }
      if (typeof data.playerId !== 'string') {
        setError('서버 응답 형식이 올바르지 않습니다.');
        return;
      }
      rememberPlayerId(normalizedCode, data.playerId);
      router.push(`/room/${normalizedCode}`);
    } catch {
      setError('네트워크 연결을 확인해주세요.');
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="appScreen">
      <section className="phonePanel homePanel" aria-labelledby="home-title">
        <h1 id="home-title">인간 발명 대회</h1>

        <form className="joinBox" onSubmit={joinRoom}>
          <label htmlFor="join-code">코드로 참여하기</label>
          <input
            id="join-code"
            inputMode="numeric"
            pattern="[0-9]*"
            value={normalizedCode}
            onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
            maxLength={6}
            placeholder="103780"
            autoComplete="one-time-code"
            disabled={pending}
          />
          <button type="submit" className="primaryButton compactButton" disabled={pending || normalizedCode.length !== 6}>
            참여하기
          </button>
        </form>

        <button type="button" className="primaryButton hostButton" onClick={createRoom} disabled={pending}>
          방 만들기
          <span>(선 플레이어 용)</span>
        </button>

        {error && <p className="errorMessage">{error}</p>}
      </section>
    </main>
  );
}

async function readJson(res: Response): Promise<Record<string, unknown>> {
  try {
    const data = await res.json();
    return isRecord(data) ? data : {};
  } catch {
    return {};
  }
}

function errorMessage(data: Record<string, unknown>, fallback: string) {
  return typeof data.error === 'string' ? data.error : fallback;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function rememberPlayerId(code: string, playerId: string) {
  try {
    localStorage.setItem(`hig:${code}:playerId`, playerId);
  } catch {
    // Storage can be unavailable in private browsing or restricted webviews.
  }
}
