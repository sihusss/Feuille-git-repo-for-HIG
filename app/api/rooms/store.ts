import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { cert, getApps, initializeApp, type App, type ServiceAccount } from 'firebase-admin/app';
import { getDatabase, type Reference } from 'firebase-admin/database';
import { partNames, parts, tileSpecs, type Part } from '../../characterParts';

export type Phase = 'lobby' | 'country' | 'creating' | 'reveal' | 'ended';

export type Tile = { id: string; part: Part; label: string; variant: string };
export type Human = { id: string; ownerId: string; tiles: Record<Part, Tile>; number?: number };
export type Player = { id: string; name: string; connectedAt: number; lastSeenAt?: number; online?: boolean };
export type Room = {
  code: string;
  countryName: string;
  hostId: string;
  players: Player[];
  phase: Phase;
  round: number;
  hands: Record<string, Record<Part, Tile[]>>;
  partOrders: Record<string, Part[]>;
  humans: Human[];
  revealAssignments: Record<string, string>;
  revealClaims: Record<string, boolean>;
  createdAt: number;
  updatedAt: number;
};

export type RoomView = Room & {
  myHuman: Human | null;
  revealedHuman: Human | null;
  maxRounds: number;
  onlineCount: number;
  offlineCount: number;
};

export type PublicRoomResult = {
  room: RoomView | null;
  etag?: string;
  notModified: boolean;
};

type LoadRoomResult = {
  room: Room | null;
  etag?: string;
  notModified?: boolean;
};

type FirebaseStore = {
  app: App;
  roomsRef: Reference;
};

declare global {
  var __humanInventionRooms: Map<string, Room> | undefined;
  var __humanInventionFirebaseStore: FirebaseStore | null | undefined;
}

const ROOM_PATH_PREFIX = 'rooms';
const FIREBASE_APP_NAME = 'human-invention-game';
const LOCAL_FIREBASE_SECRETS_FILE = 'firebase-rtdb-secrets.txt';
const MAX_CREATE_ATTEMPTS = 20;
const MAX_MUTATION_ATTEMPTS = 8;
const MAX_PLAYERS = 6;
const ONLINE_TIMEOUT_MS = 12_000;
const HEARTBEAT_WRITE_INTERVAL_MS = 4_000;
const actions = ['confirmPlayers', 'startGame', 'submitHuman', 'claimReveal', 'nextRound', 'endGame'] as const;
const rooms = globalThis.__humanInventionRooms ?? new Map<string, Room>();
globalThis.__humanInventionRooms = rooms;
let localFirebaseSecrets: Record<string, string> | undefined;

const cloneRoom = (room: Room) => JSON.parse(JSON.stringify(room)) as Room;

export async function publicRoom(code: string, viewerId?: string | null, ifNoneMatch?: string | null): Promise<PublicRoomResult> {
  const clean = cleanCode(code);
  if (!isValidCode(clean)) return { room: null, notModified: false };
  const viewer = viewerId ?? undefined;
  const heartbeatRoom = viewer ? await touchPlayerPresence(clean, viewer) : null;
  if (heartbeatRoom) {
    return { room: publicView(heartbeatRoom, viewer), etag: roomEtag(heartbeatRoom), notModified: false };
  }

  const { room, etag, notModified } = await loadRoom(clean, viewer ? undefined : ifNoneMatch ?? undefined);
  if (notModified) return { room: null, etag, notModified: true };
  return { room: room ? publicView(room, viewer) : null, etag, notModified: false };
}

export async function createRoom() {
  for (let attempt = 0; attempt < MAX_CREATE_ATTEMPTS; attempt += 1) {
    const code = makeCode();
    if ((await loadRoom(code)).room) continue;

    const now = Date.now();
    const player: Player = { id: id(), name: '선 플레이어', connectedAt: now, lastSeenAt: now };
    const room: Room = {
      code,
      countryName: '',
      hostId: player.id,
      players: [player],
      phase: 'lobby',
      round: 0,
      hands: {},
      partOrders: {},
      humans: [],
      revealAssignments: {},
      revealClaims: {},
      createdAt: now,
      updatedAt: now
    };

    try {
      await saveRoom(room, { allowOverwrite: false });
      return { room: publicView(room, player.id), playerId: player.id };
    } catch (error) {
      const existing = await loadRoom(code).catch(() => ({ room: null }));
      if (existing.room) continue;
      throw error;
    }
  }

  throw new Error('방 코드를 생성하지 못했어. 다시 시도해줘.');
}

export async function joinRoom(code: string) {
  const clean = requireCleanCode(code);
  const now = Date.now();
  const player: Player = {
    id: id(),
    name: '',
    connectedAt: now,
    lastSeenAt: now
  };

  const room = await mutateRoom(clean, (draft) => {
    if (draft.phase !== 'lobby') throw new Error('이미 시작한 방에는 들어갈 수 없어.');
    if (draft.players.length >= MAX_PLAYERS) throw new Error(`최대 ${MAX_PLAYERS}명까지 가능해.`);
    player.name = `참가자 ${draft.players.length + 1}`;
    draft.players.push(player);
  });

  return { room: publicView(room, player.id), playerId: player.id };
}

export async function action(code: string, playerId: string, type: string, payload: unknown = {}) {
  const clean = requireCleanCode(code);
  if (!playerId) throw new Error('플레이어 정보가 없어.');
  if (!type) throw new Error('액션 정보가 없어.');
  if (!knownAction(type)) throw new Error('알 수 없는 액션이야.');

  const room = await mutateRoom(clean, (draft) => {
    const player = draft.players.find((p) => p.id === playerId);
    if (!player) throw new Error('플레이어 정보가 없어.');
    player.lastSeenAt = Date.now();
    const payloadRecord = isRecord(payload) ? payload : {};

    if (type === 'confirmPlayers') {
      requireHost(draft, playerId);
      if (draft.phase !== 'lobby') throw new Error('이미 접속 완료 처리됐어.');
      draft.phase = 'country';
    }

    if (type === 'startGame') {
      requireHost(draft, playerId);
      if (draft.phase !== 'country') throw new Error('국가명 입력 단계가 아니야.');
      const countryName = cleanCountryName(payloadRecord.countryName);
      if (!countryName) throw new Error('국가명을 입력해줘.');
      draft.countryName = countryName;
      startRound(draft, 1);
    }

    if (type === 'submitHuman') {
      if (draft.phase !== 'creating') throw new Error('지금은 인간을 만들 수 없어.');
      if (draft.humans.some((h) => h.ownerId === playerId)) throw new Error('이미 완성했어.');
      const selected = isRecord(payloadRecord.tiles) ? payloadRecord.tiles : {};
      const chosen: Partial<Record<Part, Tile>> = {};

      for (const part of parts) {
        const selectedId = typeof selected[part] === 'string' ? selected[part] : '';
        const tile = draft.hands[playerId]?.[part]?.find((t) => t.id === selectedId);
        if (!tile) throw new Error(`${partNames[part]} 부위를 선택해줘.`);
        chosen[part] = tile;
      }

      draft.humans.push({ id: id(), ownerId: playerId, tiles: chosen as Record<Part, Tile> });
      if (draft.humans.length === draft.players.length) {
        draft.humans = shuffle(draft.humans).map((human, index) => ({ ...human, number: index + 1 }));
        draft.revealAssignments = makeRevealAssignments(draft);
        draft.revealClaims = {};
        draft.phase = 'reveal';
      }
    }

    if (type === 'claimReveal') {
      if (draft.phase !== 'reveal') throw new Error('아직 공개할 인간이 없어.');
      if (!draft.revealAssignments[playerId]) draft.revealAssignments = makeRevealAssignments(draft);
      if (!draft.revealAssignments[playerId]) throw new Error('공개할 인간이 없어.');
      draft.revealClaims[playerId] = true;
    }

    if (type === 'nextRound') {
      requireHost(draft, playerId);
      if (draft.phase !== 'reveal') throw new Error('공개 후에만 다음 라운드로 갈 수 있어.');
      if (draft.round >= maxRoundsFor(draft)) throw new Error('최종 라운드야. 게임을 끝내줘.');
      startRound(draft, draft.round + 1);
    }

    if (type === 'endGame') {
      requireHost(draft, playerId);
      if (draft.phase !== 'reveal') throw new Error('공개 후에만 게임을 끝낼 수 있어.');
      draft.phase = 'ended';
    }

  });

  return publicView(room, playerId);
}

async function mutateRoom(code: string, update: (room: Room) => void) {
  const clean = cleanCode(code);
  let lastError: unknown;

  for (let attempt = 0; attempt < MAX_MUTATION_ATTEMPTS; attempt += 1) {
    const { room, etag } = await loadRoom(clean);
    if (!room) throw new Error('방을 찾을 수 없어.');
    if (hasPersistentStore() && !etag) throw new Error('방 상태를 안전하게 불러오지 못했어. 다시 시도해줘.');

    const draft = cloneRoom(room);
    update(draft);
    touch(draft);

    try {
      await saveRoom(draft, { etag, allowOverwrite: true });
      return draft;
    } catch (error) {
      lastError = error;
      if (!isRetryableWriteConflict(error)) throw error;
      await waitForRetry(attempt);
    }
  }

  throw lastError instanceof Error ? lastError : new Error('방 상태 저장에 실패했어.');
}

async function touchPlayerPresence(code: string, playerId: string) {
  const clean = cleanCode(code);
  const { room } = await loadRoom(clean);
  const player = room?.players.find((candidate) => candidate.id === playerId);
  if (!room || !player) return null;

  const now = Date.now();
  const lastSeenAt = player.lastSeenAt ?? player.connectedAt;
  if (now - lastSeenAt < HEARTBEAT_WRITE_INTERVAL_MS) return room;

  return mutateRoom(clean, (draft) => {
    const current = draft.players.find((candidate) => candidate.id === playerId);
    if (current) current.lastSeenAt = now;
  });
}

async function loadRoom(code: string, ifNoneMatch?: string): Promise<LoadRoomResult> {
  if (!code) return { room: null };
  const memoryRoom = rooms.get(code);

  const firebase = firebaseStore();
  if (!firebase) {
    const etag = memoryRoom ? memoryEtag(memoryRoom) : undefined;
    if (memoryRoom && ifNoneMatch && etag && sameEtag(ifNoneMatch, etag)) {
      return { room: null, etag, notModified: true };
    }
    return { room: memoryRoom ?? null, etag };
  }

  const snapshot = await roomRef(firebase, code).get();
  if (!snapshot.exists()) {
    return { room: memoryRoom ?? null };
  }

  const value = snapshot.val();
  if (!isRecord(value)) return { room: memoryRoom ?? null };

  const room = normalizeRoom(value as Room);
  const etag = roomEtag(room);
  if (ifNoneMatch && sameEtag(ifNoneMatch, etag)) {
    return { room: null, etag, notModified: true };
  }

  rooms.set(code, room);
  return { room, etag };
}

async function saveRoom(room: Room, options: { etag?: string; allowOverwrite: boolean }) {
  const firebase = firebaseStore();
  if (!firebase) {
    rooms.set(room.code, room);
    return;
  }

  const expectedEtag = options.etag ? normalizeEtag(options.etag) : undefined;
  const result = await roomRef(firebase, room.code).transaction((current: unknown) => {
    if (!options.allowOverwrite && current) return;
    if (options.allowOverwrite && expectedEtag) {
      if (current == null) return room;
      if (!isRecord(current) || roomEtag(current as Room) !== expectedEtag) return;
    }
    return room;
  }, undefined, false);

  if (!result.committed) throw new RoomWriteConflictError();
  rooms.set(room.code, room);
}

function roomRef(firebase: FirebaseStore, code: string) {
  return firebase.roomsRef.child(cleanCode(code));
}

function hasPersistentStore() {
  return Boolean(firebaseStore());
}

function firebaseStore() {
  if (globalThis.__humanInventionFirebaseStore !== undefined) {
    return globalThis.__humanInventionFirebaseStore;
  }

  const databaseURL = normalizeFirebaseDatabaseUrl(readEnv('FIREBASE_DATABASE_URL'));
  const serviceAccount = firebaseServiceAccount();
  if (!databaseURL || !serviceAccount) {
    globalThis.__humanInventionFirebaseStore = null;
    return null;
  }

  const app = getApps().find((candidate) => candidate.name === FIREBASE_APP_NAME) ??
    initializeApp({ credential: cert(serviceAccount), databaseURL }, FIREBASE_APP_NAME);
  const store = { app, roomsRef: getDatabase(app).ref(ROOM_PATH_PREFIX) };
  globalThis.__humanInventionFirebaseStore = store;
  return store;
}

function firebaseServiceAccount(): ServiceAccount | null {
  const encodedKey = readEnv('FIREBASE_SERVICE_ACCOUNT_KEY') ?? readEnv('FIREBASE_SERVICE_ACCOUNT_JSON');
  if (encodedKey) return parseServiceAccount(encodedKey);

  const clientEmail = readEnv('FIREBASE_CLIENT_EMAIL');
  const privateKey = readEnv('FIREBASE_PRIVATE_KEY')?.replace(/\\n/g, '\n');
  if (!clientEmail || !privateKey) return null;

  return {
    projectId: readEnv('FIREBASE_PROJECT_ID'),
    clientEmail,
    privateKey
  };
}

function parseServiceAccount(value: string): ServiceAccount {
  const trimmed = value.trim();
  const json = trimmed.startsWith('{') ? trimmed : Buffer.from(trimmed, 'base64').toString('utf8');

  try {
    const parsed = JSON.parse(json) as Record<string, unknown>;
    const clientEmail = stringValue(parsed.client_email) ?? stringValue(parsed.clientEmail);
    const privateKey = (stringValue(parsed.private_key) ?? stringValue(parsed.privateKey))?.replace(/\\n/g, '\n');
    if (!clientEmail || !privateKey) throw new Error('missing service account fields');

    return {
      projectId: stringValue(parsed.project_id) ?? stringValue(parsed.projectId),
      clientEmail,
      privateKey
    };
  } catch {
    throw new Error('Firebase 서비스 계정 환경변수가 올바르지 않아.');
  }
}

function normalizeFirebaseDatabaseUrl(value?: string) {
  if (!value) return undefined;

  try {
    const url = new URL(value);
    if (url.hostname.endsWith('.firebase.app')) {
      url.hostname = url.hostname.replace(/\.firebase\.app$/, '.firebasedatabase.app');
    }
    return url.toString().replace(/\/$/, '');
  } catch {
    return value;
  }
}

function stringValue(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

function readEnv(name: string) {
  const value = process.env[name] ?? readLocalFirebaseSecret(name);
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

function readLocalFirebaseSecret(name: string) {
  if (!name.startsWith('FIREBASE_')) return undefined;
  return loadLocalFirebaseSecrets()[name];
}

function loadLocalFirebaseSecrets() {
  if (localFirebaseSecrets !== undefined) return localFirebaseSecrets;

  const values: Record<string, string> = {};
  try {
    const content = readFileSync(join(process.cwd(), LOCAL_FIREBASE_SECRETS_FILE), 'utf8');
    const lines = content.split(/\r?\n/);

    for (let index = 0; index < lines.length; index += 1) {
      const match = lines[index].match(/^([A-Z0-9_]+)=(.*)$/);
      if (!match) continue;

      const key = match[1];
      let value = match[2].trim();
      let balance = braceBalance(value);

      if (value.startsWith('{') && balance > 0) {
        const block = [value];
        while (balance > 0 && index + 1 < lines.length) {
          index += 1;
          block.push(lines[index]);
          balance += braceBalance(lines[index]);
        }
        value = block.join('\n');
      }

      values[key] = unquoteEnvValue(value);
    }
  } catch {
    // Local fallback is optional; deployed environments should use real env vars.
  }

  localFirebaseSecrets = values;
  return values;
}

function braceBalance(value: string) {
  let balance = 0;
  for (const character of value) {
    if (character === '{') balance += 1;
    if (character === '}') balance -= 1;
  }
  return balance;
}

function unquoteEnvValue(value: string) {
  const trimmed = value.trim();
  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function isRetryableWriteConflict(error: unknown) {
  return error instanceof RoomWriteConflictError;
}

class RoomWriteConflictError extends Error {}

function normalizeRoom(room: Room): Room {
  return {
    ...room,
    countryName: typeof room.countryName === 'string' ? room.countryName : '',
    players: Array.isArray(room.players) ? room.players : [],
    phase: room.phase ?? 'lobby',
    round: typeof room.round === 'number' ? room.round : 0,
    hands: isRecord(room.hands) ? room.hands as Record<string, Record<Part, Tile[]>> : {},
    partOrders: isRecord(room.partOrders) ? room.partOrders as Record<string, Part[]> : {},
    humans: Array.isArray(room.humans) ? room.humans : [],
    revealAssignments: isRecord(room.revealAssignments) ? room.revealAssignments as Record<string, string> : {},
    revealClaims: isRecord(room.revealClaims) ? room.revealClaims as Record<string, boolean> : {},
    createdAt: typeof room.createdAt === 'number' ? room.createdAt : Date.now(),
    updatedAt: typeof room.updatedAt === 'number' ? room.updatedAt : Date.now()
  };
}

function publicView(room: Room, viewerId?: string): RoomView {
  const safe = cloneRoom(room) as RoomView;
  const now = Date.now();
  const isPlayer = Boolean(viewerId && safe.players.some((p) => p.id === viewerId));
  const assignedHumanId = viewerId ? safe.revealAssignments[viewerId] : undefined;
  const hasClaimedReveal = Boolean(viewerId && safe.revealClaims[viewerId]);

  safe.players = safe.players.map((player) => ({
    ...player,
    lastSeenAt: player.lastSeenAt ?? player.connectedAt,
    online: isOnline(player, now)
  }));
  safe.hands = isPlayer && viewerId && safe.hands[viewerId] ? { [viewerId]: safe.hands[viewerId] } : {};
  safe.partOrders = isPlayer && viewerId && safe.partOrders[viewerId] ? { [viewerId]: safe.partOrders[viewerId] } : {};
  safe.myHuman = viewerId ? safe.humans.find((human) => human.ownerId === viewerId) ?? null : null;
  safe.revealedHuman = hasClaimedReveal && assignedHumanId ? safe.humans.find((human) => human.id === assignedHumanId) ?? null : null;
  safe.maxRounds = maxRoundsFor(room);
  safe.onlineCount = safe.players.filter((player) => player.online).length;
  safe.offlineCount = safe.players.length - safe.onlineCount;
  safe.revealAssignments = hasClaimedReveal && viewerId && assignedHumanId ? { [viewerId]: assignedHumanId } : {};
  safe.revealClaims = hasClaimedReveal && viewerId ? { [viewerId]: true } : {};

  if (safe.phase !== 'ended') {
    safe.humans = [];
  }

  return safe;
}

function startRound(room: Room, round: number) {
  room.round = round;
  room.phase = 'creating';
  room.hands = {};
  room.partOrders = {};
  room.humans = [];
  room.revealAssignments = {};
  room.revealClaims = {};

  for (const player of room.players) {
    room.hands[player.id] = makeHand();
    room.partOrders[player.id] = shuffle(parts);
  }
}

function makeHand() {
  const hand = {} as Record<Part, Tile[]>;
  for (const part of parts) {
    hand[part] = shuffle(tileSpecs[part]).slice(0, 4).map((tile) => ({ ...tile, part, id: `${part}-${id()}` }));
  }
  return hand;
}

function makeRevealAssignments(room: Room) {
  const assignments: Record<string, string> = {};
  const playersWithHumans = shuffle(room.players.filter((player) => room.humans.some((human) => human.ownerId === player.id)));
  const humansByOwner = new Map(room.humans.map((human) => [human.ownerId, human]));

  if (playersWithHumans.length === 0) return assignments;
  if (playersWithHumans.length === 1) {
    const onlyPlayer = playersWithHumans[0];
    const onlyHuman = humansByOwner.get(onlyPlayer.id);
    if (onlyHuman) assignments[onlyPlayer.id] = onlyHuman.id;
    return assignments;
  }

  const offset = randomInt(playersWithHumans.length - 1) + 1;
  const orderedHumans = playersWithHumans.map((player) => humansByOwner.get(player.id)).filter(Boolean) as Human[];

  for (let index = 0; index < playersWithHumans.length; index += 1) {
    assignments[playersWithHumans[index].id] = orderedHumans[(index + offset) % orderedHumans.length].id;
  }

  return assignments;
}

function isOnline(player: Player, now = Date.now()) {
  return now - (player.lastSeenAt ?? player.connectedAt) <= ONLINE_TIMEOUT_MS;
}

function maxRoundsFor(room: Room) {
  return Math.max(1, room.players.length * 2);
}

function shuffle<T>(items: readonly T[]) {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = randomInt(index + 1);
    [shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
  }
  return shuffled;
}

function makeCode() {
  return String(100000 + randomInt(900000));
}

function id() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now().toString(36)}-${randomInt(36 ** 8).toString(36)}`;
}

function randomInt(maxExclusive: number) {
  if (maxExclusive <= 0) return 0;
  const crypto = globalThis.crypto;
  if (crypto?.getRandomValues) {
    const limit = Math.floor(0x1_0000_0000 / maxExclusive) * maxExclusive;
    const values = new Uint32Array(1);
    do {
      crypto.getRandomValues(values);
    } while (values[0] >= limit);
    return values[0] % maxExclusive;
  }
  return Math.floor(Math.random() * maxExclusive);
}

function cleanCode(code: string) {
  return String(code ?? '').replace(/\D/g, '').slice(0, 6);
}

function requireCleanCode(code: string) {
  const clean = cleanCode(code);
  if (!isValidCode(clean)) throw new Error('6자리 참가 코드가 올바르지 않아.');
  return clean;
}

function isValidCode(code: string) {
  return /^\d{6}$/u.test(code);
}

function cleanCountryName(value: unknown) {
  return String(value ?? '').trim().replace(/국$/u, '').slice(0, 12);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function knownAction(type: string) {
  return (actions as readonly string[]).includes(type);
}

function memoryEtag(room: Room) {
  return roomEtag(room);
}

function roomEtag(room: Room) {
  return `room-${room.updatedAt}`;
}

export function etagForRoom(room: Pick<Room, 'updatedAt'>) {
  return `room-${room.updatedAt}`;
}

function sameEtag(left: string, right: string) {
  return normalizeEtag(left) === normalizeEtag(right);
}

function normalizeEtag(value: string) {
  return value.trim().replace(/^W\//u, '');
}

function waitForRetry(attempt: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, 25 * (attempt + 1) + randomInt(35));
  });
}

function touch(room: Room) {
  room.updatedAt = Date.now();
}

function requireHost(room: Room, playerId: string) {
  if (room.hostId !== playerId) throw new Error('선 플레이어만 할 수 있어.');
}
