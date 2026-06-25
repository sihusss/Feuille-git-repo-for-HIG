'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { assetPathForPart, partAssetSpecs, partNames, parts, type Part } from '../../characterParts';

type Phase = 'lobby' | 'country' | 'creating' | 'reveal' | 'ended';
type Tile = { id: string; part: Part; label: string; variant?: string; emoji?: string };
type Human = {
  id: string;
  ownerId: string;
  tiles: Record<Part, Tile>;
  number?: number;
  round?: number;
  successScore?: number;
  viewerVoted?: boolean;
};
type Player = { id: string; name: string; connectedAt: number; lastSeenAt?: number; online?: boolean };
type Room = {
  code: string;
  countryName: string;
  hostId: string;
  players: Player[];
  phase: Phase;
  round: number;
  hands: Record<string, Record<Part, Tile[]>>;
  partOrders: Record<string, Part[]>;
  humans: Human[];
  archivedHumans: Human[];
  revealAssignments: Record<string, string>;
  revealClaims: Record<string, boolean>;
  successVotes: Record<string, Record<string, boolean>>;
  myHuman: Human | null;
  revealedHuman: Human | null;
  revealedCount: number;
  requiredRevealCount: number;
  maxRounds: number;
  onlineCount: number;
  offlineCount: number;
  successfulHumans: Human[];
};

const pollDelays: Record<Phase | 'loading', number> = {
  loading: 1200,
  lobby: 2500,
  country: 1500,
  creating: 1500,
  reveal: 1000,
  ended: 10000
};

const humanLayerOrder = ['lower', 'upper', 'head', 'hair'] as const satisfies readonly Part[];
const humanCondition = '성격 + 인기 또는 사회적 지위';
const successQuestions = [
  '이 아이는 어떤 성격 때문에 가장 사랑받았을까?',
  '인기나 사회적 지위는 어디에서 생겼을까?',
  '이 아이가 모두에게 인정받은 결정적 순간은 무엇이었을까?'
] as const;

export default function GameClient({ code }: { code: string }) {
  const [room, setRoom] = useState<Room | null>(null);
  const [playerId, setPlayerId] = useState('');
  const [playerReady, setPlayerReady] = useState(false);
  const [error, setError] = useState('');
  const [loadError, setLoadError] = useState('');
  const [countryName, setCountryName] = useState('');
  const [selected, setSelected] = useState<Partial<Record<Part, string>>>({});
  const [creationStarted, setCreationStarted] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [roomLink, setRoomLink] = useState('');
  const [shareMessage, setShareMessage] = useState('');
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [joining, setJoining] = useState(false);
  const actionInFlight = useRef(false);
  const joinInFlight = useRef(false);
  const roomEtag = useRef('');

  useEffect(() => {
    setPlayerReady(false);
    roomEtag.current = '';
    const stored = readStoredPlayerId(code);
    setPlayerId(stored ?? '');
    setRoomLink(`${window.location.origin}/room/${code}`);
    setPlayerReady(true);
  }, [code]);

  useEffect(() => {
    if (!playerReady) return;

    let alive = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let controller: AbortController | undefined;

    async function load() {
      let nextDelayPhase = room?.phase;
      try {
        controller = new AbortController();
        const query = playerId ? `?playerId=${encodeURIComponent(playerId)}` : '';
        const headers = roomEtag.current ? { 'If-None-Match': roomEtag.current } : undefined;
        const res = await fetch(`/api/rooms/${code}${query}`, { cache: 'no-store', headers, signal: controller.signal });
        if (!alive) return;

        if (res.status === 304) {
          setLoadError('');
          return;
        }

        const data = await readJson(res);
        if (!alive) return;
        if (res.ok) {
          if (isRecord(data.room)) {
            const nextRoom = data.room as Room;
            nextDelayPhase = nextRoom.phase;
            roomEtag.current = res.headers.get('etag') ?? roomEtag.current;
            setRoom(nextRoom);
            setLoadError('');
          } else {
            setLoadError('서버 응답 형식이 올바르지 않아.');
          }
        } else {
          setLoadError(errorMessage(data, '방을 불러오지 못했어.'));
        }
      } catch (e) {
        if (alive && !isAbortError(e)) setLoadError('네트워크 연결을 확인해줘.');
      } finally {
        if (alive) {
          timer = setTimeout(load, pollDelayFor(nextDelayPhase));
        }
      }
    }

    load();
    return () => {
      alive = false;
      controller?.abort();
      if (timer) clearTimeout(timer);
    };
  }, [code, playerId, playerReady, room?.phase]);

  const me = room?.players.find((player) => player.id === playerId) ?? null;
  const isHost = room?.hostId === playerId;
  const myHand = playerId && room?.hands[playerId] ? room.hands[playerId] : null;
  const myOrder = playerId && room?.partOrders[playerId] ? room.partOrders[playerId] : [];
  const currentPart = myOrder[stepIndex];
  const selectedTiles = useMemo(() => {
    if (!myHand) return null;
    const entries = parts.map((part) => {
      const tile = myHand[part]?.find((candidate) => candidate.id === selected[part]);
      return tile ? [part, tile] : null;
    });
    if (entries.some((entry) => !entry)) return null;
    return Object.fromEntries(entries as [Part, Tile][]) as Record<Part, Tile>;
  }, [myHand, selected]);
  const isFinalRound = room ? room.round >= room.maxRounds : false;

  useEffect(() => {
    setSelected({});
    setCreationStarted(false);
    setStepIndex(0);
    setError('');
  }, [room?.round]);

  useEffect(() => {
    if (room?.countryName) setCountryName(room.countryName);
  }, [room?.countryName]);

  async function doAction(type: string, payload?: unknown) {
    if (actionInFlight.current) return;
    if (!playerId) {
      setError('플레이어 정보가 없어.');
      return;
    }
    actionInFlight.current = true;
    setPendingAction(type);
    setError('');

    try {
      const res = await fetch(`/api/rooms/${code}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ playerId, type, payload })
      });
      const data = await readJson(res);
      if (!res.ok) {
        setError(errorMessage(data, '처리 실패'));
        return;
      }
      if (!isRecord(data.room)) {
        setError('서버 응답 형식이 올바르지 않아.');
        return;
      }
      roomEtag.current = res.headers.get('etag') ?? roomEtag.current;
      setRoom(data.room as Room);
    } catch {
      setError('네트워크 연결을 확인해줘.');
    } finally {
      actionInFlight.current = false;
      setPendingAction(null);
    }
  }

  async function joinFromLink() {
    if (joinInFlight.current) return;
    joinInFlight.current = true;
    setJoining(true);
    setError('');

    try {
      const res = await fetch(`/api/rooms/${code}/join`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await readJson(res);
      if (!res.ok) {
        setError(errorMessage(data, '입장 실패'));
        return;
      }
      if (typeof data.playerId !== 'string' || !isRecord(data.room)) {
        setError('서버 응답 형식이 올바르지 않아.');
        return;
      }
      rememberPlayerId(code, data.playerId);
      setPlayerId(data.playerId);
      roomEtag.current = res.headers.get('etag') ?? roomEtag.current;
      setRoom(data.room as Room);
    } catch {
      setError('네트워크 연결을 확인해줘.');
    } finally {
      joinInFlight.current = false;
      setJoining(false);
    }
  }

  async function shareRoom() {
    if (!roomLink) return;
    setShareMessage('');
    try {
      if (navigator.share) {
        await navigator.share({ title: '인간 발명 대회', text: `참가 코드: ${code}`, url: roomLink });
        return;
      }
      await navigator.clipboard.writeText(roomLink);
      setShareMessage('초대 링크를 복사했어.');
    } catch {
      setShareMessage(roomLink);
    }
  }

  function confirmTopScoreAndContinue() {
    const confirmed = window.confirm('최득점 인간을 확정하고 다음 라운드로 넘어갈까?');
    if (confirmed) void doAction('nextRound');
  }

  if (!room) {
    return (
      <main className="appScreen">
        <section className="phonePanel messagePanel" aria-live="polite" aria-busy={!loadError}>
          <p role={loadError ? 'alert' : 'status'}>{loadError || '방 불러오는 중...'}</p>
          {loadError && <Link className="secondaryLink" href="/">홈으로</Link>}
        </section>
      </main>
    );
  }

  if (!me) {
    return (
      <main className="appScreen">
        <section className="phonePanel joinRoomPanel" aria-labelledby="join-room-title" aria-busy={joining}>
          <h1 id="join-room-title">인간 발명 대회</h1>
          <p className="codeLine">참가 코드: {room.code}</p>
          {room.phase === 'lobby' ? (
            <button type="button" className="primaryButton bottomButton" onClick={joinFromLink} disabled={joining}>
              {joining ? '참여 중' : '참여하기'}
            </button>
          ) : (
            <Link className="primaryButton bottomButton mutedButton" href="/">
              이미 시작됨
            </Link>
          )}
          {error && <p className="errorMessage" role="alert">{error}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="appScreen">
      <section className="phonePanel gamePanel">
        {room.phase === 'lobby' && (
          <LobbyView
            room={room}
            isHost={Boolean(isHost)}
            shareMessage={shareMessage}
            busy={Boolean(pendingAction)}
            onShare={shareRoom}
            onConfirm={() => doAction('confirmPlayers')}
          />
        )}

        {room.phase === 'country' && (
          <CountryView
            isHost={Boolean(isHost)}
            countryName={countryName}
            busy={Boolean(pendingAction)}
            onCountryName={setCountryName}
            onStart={() => doAction('startGame', { countryName })}
          />
        )}

        {room.phase === 'creating' && myHand && (
          <CreationView
            room={room}
            myHand={myHand}
            currentPart={currentPart}
            creationStarted={creationStarted}
            stepIndex={stepIndex}
            selected={selected}
            selectedTiles={selectedTiles}
            busy={Boolean(pendingAction)}
            onBegin={() => setCreationStarted(true)}
            onSelect={(part, tileId) => setSelected((current) => ({ ...current, [part]: tileId }))}
            onConfirmPart={() => setStepIndex((current) => Math.min(current + 1, parts.length))}
            onSubmit={() => selectedTiles && doAction('submitHuman', { tiles: selected })}
          />
        )}

        {room.phase === 'reveal' && (
          <RevealView
            room={room}
            isHost={Boolean(isHost)}
            isFinalRound={isFinalRound}
            busy={Boolean(pendingAction)}
            onReveal={() => doAction('claimReveal')}
            onVote={() => doAction('voteSuccess')}
            onNext={confirmTopScoreAndContinue}
            onEnd={() => doAction('endGame')}
          />
        )}

        {room.phase === 'ended' && (
          <EndedView room={room} />
        )}

        {error && <p className="errorMessage floatingError" role="alert">{error}</p>}
      </section>
    </main>
  );
}

function LobbyView({
  room,
  isHost,
  shareMessage,
  busy,
  onShare,
  onConfirm
}: {
  room: Room;
  isHost: boolean;
  shareMessage: string;
  busy: boolean;
  onShare: () => void;
  onConfirm: () => void;
}) {
  const onlineCount = typeof room.onlineCount === 'number'
    ? room.onlineCount
    : room.players.filter((player) => player.online !== false).length;
  const offlineCount = typeof room.offlineCount === 'number'
    ? room.offlineCount
    : room.players.length - onlineCount;

  return (
    <section className="centerStack" aria-labelledby="lobby-title">
      <h1 id="lobby-title">인간 발명 대회</h1>
      <p className="codeLine">참가 코드: {room.code}</p>
      <div className="presencePanel" aria-label="참가자 접속 상태" aria-live="polite">
        <p className="playerCount">총 {room.players.length}명 · 온라인 {onlineCount}명 · 오프라인 {offlineCount}명</p>
        <div className="presenceList">
          {room.players.map((player) => (
            <span key={player.id} className={player.online === false ? 'presencePill offline' : 'presencePill online'}>
              <span aria-hidden="true" />
              {player.name}
            </span>
          ))}
        </div>
      </div>
      <button type="button" className="secondaryButton" onClick={onShare}>초대 링크 공유</button>
      {shareMessage && <p className="hintText" role="status">{shareMessage}</p>}
      {isHost ? (
        <button type="button" className="primaryButton bottomButton" onClick={onConfirm} disabled={busy}>
          {busy ? '처리 중' : '모두 접속 완료'}
        </button>
      ) : (
        <p className="bottomNotice">선 플레이어가 시작할 때까지 기다려.</p>
      )}
    </section>
  );
}

function CountryView({
  isHost,
  countryName,
  busy,
  onCountryName,
  onStart
}: {
  isHost: boolean;
  countryName: string;
  busy: boolean;
  onCountryName: (value: string) => void;
  onStart: () => void;
}) {
  if (!isHost) {
    return (
      <section className="centerStack" aria-labelledby="country-wait-title">
        <h1 id="country-wait-title">국가 준비</h1>
        <p className="hintText">선 플레이어가 국가명을 입력하는 중이야.</p>
      </section>
    );
  }

  return (
    <section className="centerStack" aria-labelledby="country-title" aria-busy={busy}>
      <div className="countryForm">
        <label id="country-title" htmlFor="country-name">국가명</label>
        <div className="suffixInput">
          <input
            id="country-name"
            value={countryName}
            onChange={(event) => onCountryName(event.target.value.replace(/국$/u, '').slice(0, 12))}
            maxLength={12}
            placeholder="말랑"
            aria-describedby="country-name-suffix"
            disabled={busy}
          />
          <span id="country-name-suffix" aria-hidden="true">국</span>
        </div>
      </div>
      <button type="button" className="primaryButton bottomButton" disabled={busy || !countryName.trim()} onClick={onStart}>
        {busy ? '시작 중' : '게임 시작'}
      </button>
    </section>
  );
}

function CreationView({
  room,
  myHand,
  currentPart,
  creationStarted,
  stepIndex,
  selected,
  selectedTiles,
  busy,
  onBegin,
  onSelect,
  onConfirmPart,
  onSubmit
}: {
  room: Room;
  myHand: Record<Part, Tile[]>;
  currentPart: Part | undefined;
  creationStarted: boolean;
  stepIndex: number;
  selected: Partial<Record<Part, string>>;
  selectedTiles: Record<Part, Tile> | null;
  busy: boolean;
  onBegin: () => void;
  onSelect: (part: Part, tileId: string) => void;
  onConfirmPart: () => void;
  onSubmit: () => void;
}) {
  if (room.myHuman) {
    return (
      <RevealGate busy disabled hint="다른 참가자가 완성하면 공개할 수 있어." />
    );
  }

  if (!creationStarted) {
    return (
      <section className="centerStack" aria-labelledby="creation-ready-title">
        <h1 id="creation-ready-title" className="srOnly">{room.round}라운드 인간 창조</h1>
        <p className="conditionBadge">{humanCondition}</p>
        <button type="button" className="primaryButton bigCenterButton" onClick={onBegin}>
          {room.round}라운드 인간 창조
        </button>
      </section>
    );
  }

  if (currentPart) {
    const currentSelected = selected[currentPart];
    const currentTiles = myHand[currentPart] ?? [];

    return (
      <section className="partSelectView" aria-labelledby="part-title">
        <h1 id="part-title">{partNames[currentPart]}</h1>
        <div className="partGrid" role="group" aria-label={`${partNames[currentPart]} 선택`}>
          {currentTiles.map((tile) => (
            <button
              key={tile.id}
              type="button"
              className={currentSelected === tile.id ? 'partTile selected' : 'partTile'}
              onClick={() => onSelect(currentPart, tile.id)}
              aria-pressed={currentSelected === tile.id}
            >
              <PartPreview tile={tile} />
              <small>{tile.label}</small>
              {currentSelected === tile.id && <span className="srOnly">선택됨</span>}
            </button>
          ))}
        </div>
        <p className="progressText" aria-live="polite">{stepIndex + 1} / {parts.length}</p>
        <button type="button" className="primaryButton bottomButton" disabled={!currentSelected} onClick={onConfirmPart}>
          확인
        </button>
      </section>
    );
  }

  return (
    <section className="centerStack" aria-busy={busy}>
      <p className="conditionBadge">{humanCondition}</p>
      {selectedTiles ? <HumanFigure tiles={selectedTiles} /> : <div className="mysteryHuman">?</div>}
      <button type="button" className="primaryButton bottomButton" disabled={busy || !selectedTiles} onClick={onSubmit}>
        {busy ? '완성 중' : '인간 완성'}
      </button>
    </section>
  );
}

function RevealView({
  room,
  isHost,
  isFinalRound,
  busy,
  onReveal,
  onVote,
  onNext,
  onEnd
}: {
  room: Room;
  isHost: boolean;
  isFinalRound: boolean;
  busy: boolean;
  onReveal: () => void;
  onVote: () => void;
  onNext: () => void;
  onEnd: () => void;
}) {
  const allRevealed = room.requiredRevealCount > 0 && room.revealedCount >= room.requiredRevealCount;

  if (!room.revealedHuman) {
    return <RevealGate busy={busy} onReveal={onReveal} />;
  }

  return (
    <section className="revealView" aria-busy={busy}>
      <HumanReveal human={room.revealedHuman} />
      <SuccessVote
        human={room.revealedHuman}
        busy={busy}
        onVote={onVote}
      />
      <div className="revealActions">
        <button type="button" className={isFinalRound || !allRevealed ? 'secondaryButton' : 'primaryButton'} disabled={busy || isFinalRound || !allRevealed} onClick={onNext}>
          {busy ? '처리 중' : isFinalRound ? '최종 라운드' : allRevealed ? '최득점' : '공개 대기'}
        </button>
        {isHost ? (
          <button type="button" className={isFinalRound ? 'primaryButton endButton activeEnd' : 'secondaryButton endButton'} disabled={busy} onClick={onEnd}>
            {busy ? '처리 중' : '게임 끝'}
          </button>
        ) : (
          <p className="hintText revealHostHint">
            {allRevealed ? '누구든 최득점을 확정하면 다음 라운드로 넘어가.' : '모두 공개하면 최득점을 확정할 수 있어.'}
          </p>
        )}
      </div>
    </section>
  );
}

function SuccessVote({
  human,
  busy,
  onVote
}: {
  human: Human;
  busy: boolean;
  onVote: () => void;
}) {
  const score = human.successScore ?? 0;
  const voted = Boolean(human.viewerVoted);

  return (
    <div className="successVote" aria-live="polite">
      <p>{score}명이 성공한 인간으로 봤어.</p>
      <button type="button" className="secondaryButton successButton" disabled={busy || voted} onClick={onVote}>
        {voted ? '성공 인정 완료' : '성공!'}
      </button>
    </div>
  );
}

function EndedView({ room }: { room: Room }) {
  const winners = room.successfulHumans ?? [];

  return (
    <section className="endedView" aria-labelledby="ended-title">
      <div className="endedHeader">
        <h1 id="ended-title">게임 끝</h1>
        <p className="countryBadge">{room.countryName}국의 인간 발명이 완료됐어.</p>
      </div>

      <section className="hallOfFame" aria-labelledby="hall-title">
        <h2 id="hall-title">성공한 아이들</h2>
        {winners.length > 0 ? (
          <div className="successList">
            {winners.map((human, index) => (
              <SuccessHumanCard key={human.id} human={human} rank={index + 1} />
            ))}
          </div>
        ) : (
          <p className="hintText">아직 성공 표를 받은 인간이 없어.</p>
        )}
      </section>

      <section className="questionPanel" aria-labelledby="question-title">
        <h2 id="question-title">질문</h2>
        <ul>
          {successQuestions.map((question) => (
            <li key={question}>{question}</li>
          ))}
        </ul>
      </section>

      <Link className="primaryButton bottomButton" href="/">새 방 만들기</Link>
    </section>
  );
}

function SuccessHumanCard({ human, rank }: { human: Human; rank: number }) {
  return (
    <article className="successCard" aria-label={`${rank}위 인간`}>
      <div className="successMeta">
        <span className="rankBadge">{rank}위</span>
        <span>{human.round ?? '?'}라운드 · {human.number ?? '?'}번</span>
        <strong>{human.successScore ?? 0}표</strong>
      </div>
      <HumanFigure tiles={human.tiles} />
      <TraitList tiles={human.tiles} />
    </article>
  );
}

function RevealGate({
  busy,
  disabled = false,
  hint,
  onReveal
}: {
  busy: boolean;
  disabled?: boolean;
  hint?: string;
  onReveal?: () => void;
}) {
  return (
    <section className="centerStack revealGate">
      <div className="mysteryHuman" role="img" aria-label="아직 공개되지 않은 인간">?</div>
      <button type="button" className="primaryButton bigCenterButton" onClick={onReveal} disabled={busy || disabled || !onReveal}>
        {busy ? '공개 중' : '인간 공개'}
      </button>
      {hint && <p className="hintText">{hint}</p>}
    </section>
  );
}

function HumanReveal({ human }: { human: Human }) {
  return (
    <article className="humanReveal" aria-label={`${human.number ?? ''}번 인간`}>
      <div className="revealPortrait">
        <span className="numberBadge topBadge" aria-hidden="true">{human.number}</span>
        <HumanFigure tiles={human.tiles} />
        <span className="numberBadge bottomBadge" aria-hidden="true">{human.number}</span>
      </div>
      <TraitList tiles={human.tiles} />
    </article>
  );
}

function TraitList({ tiles }: { tiles: Record<Part, Tile> }) {
  return (
    <dl className="traitList" aria-label="인간 묘사">
      {parts.map((part) => (
        <div key={part} className={`traitItem trait-${part}`}>
          <dt>{partNames[part]}</dt>
          <dd>{tiles[part].label}</dd>
        </div>
      ))}
    </dl>
  );
}

function HumanFigure({ tiles }: { tiles: Record<Part, Tile> }) {
  const description = parts.map((part) => tiles[part].label).join(', ');

  return (
    <figure className="humanFigure" role="img" aria-label={`${description}`}>
      {humanLayerOrder.map((part) => {
        const asset = assetForTile(tiles[part], part);
        return (
          <img
            key={part}
            className={`humanPartImage human-${part}`}
            src={asset.src}
            alt=""
            draggable={false}
          />
        );
      })}
    </figure>
  );
}

function PartPreview({ tile }: { tile: Tile }) {
  const asset = assetForTile(tile, tile.part);

  return (
    <div className="partPreview" aria-hidden="true">
      <img className={`partPreviewImage preview-${tile.part}`} src={asset.src} alt="" draggable={false} />
    </div>
  );
}

type CharacterAsset = {
  src: string;
};

function assetForTile(tile: Tile, part: Part): CharacterAsset {
  const spec = partAssetSpecs[part];
  const variant = tile.variant ?? '';
  const match = new RegExp(`^${spec.variantPrefix}-(\\d+)$`).exec(variant);
  const rawIndex = match ? Number(match[1]) : stableHash(tile.id || tile.label) % spec.count;
  const index = Number.isFinite(rawIndex) ? Math.min(Math.max(rawIndex, 0), spec.count - 1) : 0;
  return { src: assetPathForPart(part, index) };
}

function stableHash(input: string) {
  let hash = 0;
  for (let index = 0; index < input.length; index += 1) {
    hash = (hash * 31 + input.charCodeAt(index)) >>> 0;
  }
  return hash;
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

function pollDelayFor(phase?: Phase) {
  return phase ? pollDelays[phase] : pollDelays.loading;
}

function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === 'AbortError';
}

function readStoredPlayerId(code: string) {
  try {
    return localStorage.getItem(`hig:${code}:playerId`);
  } catch {
    return null;
  }
}

function rememberPlayerId(code: string, playerId: string) {
  try {
    localStorage.setItem(`hig:${code}:playerId`, playerId);
  } catch {
    // Storage can be unavailable in private browsing or restricted webviews.
  }
}
