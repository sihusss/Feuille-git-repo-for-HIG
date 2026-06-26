export const parts = ['head', 'arms', 'torso', 'legs'] as const;

export type Part = typeof parts[number];

export type TileSpec = {
  label: string;
  variant: string;
};

export type PartAssetSpec = {
  directory: string;
  filePrefix: string;
  fileExtension: 'svg';
  variantPrefix: string;
  count: number;
};

export const CHARACTER_ASSET_BASE = '/assets/model_parts';
export const CHARACTER_CANVAS_RATIO = '512 / 682';
export const characterLayerOrder = ['legs', 'arms', 'torso', 'head'] as const satisfies readonly Part[];

export const partNames: Record<Part, string> = {
  head: '머리',
  arms: '팔',
  torso: '몸',
  legs: '하체'
};

export const partAssetSpecs: Record<Part, PartAssetSpec> = {
  head: {
    directory: 'heads',
    filePrefix: 'head_',
    fileExtension: 'svg',
    variantPrefix: 'head',
    count: 24
  },
  arms: {
    directory: 'arms',
    filePrefix: 'arms_',
    fileExtension: 'svg',
    variantPrefix: 'arms',
    count: 24
  },
  torso: {
    directory: 'torsos',
    filePrefix: 'torso_',
    fileExtension: 'svg',
    variantPrefix: 'torso',
    count: 24
  },
  legs: {
    directory: 'legs',
    filePrefix: 'legs_',
    fileExtension: 'svg',
    variantPrefix: 'legs',
    count: 24
  }
};

const partLabels: Record<Part, readonly string[]> = {
  head: [
    '기본 타원형 머리',
    '짧은 직모 머리',
    '둥근 곱슬 머리',
    '위쪽 묶음 머리',
    '밝은 앞머리',
    '짙은 단발 머리',
    '갈색 양갈래 머리',
    '은색 둥근 머리',
    '긴 검은 머리',
    '금색 보브 머리',
    '짙은 곱슬 머리',
    '작은 묶음 머리',
    '밝은 둥근 머리',
    '검은 앞머리',
    '갈색 곱슬 머리',
    '남색 단정 머리',
    '짙은 타원형 머리',
    '금색 짧은 머리',
    '검은 둥근 머리',
    '갈색 상투 머리',
    '흰색 볼륨 머리',
    '차분한 보브 머리',
    '금색 곱슬 머리',
    '남색 둥근 머리'
  ],
  arms: [
    '편한 내린 팔',
    '바깥 제스처 팔',
    '앞으로 모은 팔',
    '한쪽 굽힌 팔',
    '낮은 안내 팔',
    '몸 앞으로 모은 팔',
    '곧게 내린 팔',
    '넓게 펼친 팔',
    '비대칭 내린 팔',
    '손짓하는 팔',
    '손 모은 팔',
    '좁게 내린 팔',
    '가로 설명 팔',
    '높이 든 팔',
    '기본 세운 팔',
    '작은 손짓 팔',
    '차분한 내린 팔',
    '한쪽 수평 팔',
    '환영하는 팔',
    '짙은 내린 팔',
    '엇갈린 팔',
    '양손 모은 팔',
    '한손 안내 팔',
    '소극적 손짓 팔'
  ],
  torso: [
    '기본 가디건',
    '줄무늬 티셔츠',
    '짙은 재킷',
    '포켓 조끼',
    '흰 셔츠',
    '트랙 상의',
    '긴 코트',
    '니트 상의',
    '데님 상의',
    '줄무늬 스웨터',
    '검은 재킷',
    '회색 블레이저',
    '트렌치 상의',
    '짧은 니트',
    '파란 셔츠',
    '리넨 셔츠',
    '스웨이드 재킷',
    '차콜 블레이저',
    '바시티 상의',
    '윈드브레이커',
    '캠프 셔츠',
    '러스트 셔츠',
    '후디 상의',
    '가죽 재킷'
  ],
  legs: [
    '검은 바지',
    '파란 치마',
    '데님 반바지',
    '검은 부츠 하체',
    '회색 조거',
    '짙은 치마',
    '남색 크롭 바지',
    '카고 바지',
    '와이드 데님',
    '러닝 반바지',
    '회색 치마',
    '올리브 바지',
    '밝은 반바지',
    '아이보리 카고',
    '검은 치마',
    '하늘색 카고',
    '다크 데님',
    '검은 조거',
    '붉은 치마',
    '검은 카고 부츠',
    '아이보리 치마',
    '검은 와이드 바지',
    '밝은 데님',
    '네이비 반바지'
  ]
};

export function assetPathForPart(part: Part, index: number) {
  const spec = partAssetSpecs[part];
  const safeIndex = clampAssetIndex(index, spec.count);
  return `${CHARACTER_ASSET_BASE}/${spec.directory}/${spec.filePrefix}${safeIndex}.${spec.fileExtension}`;
}

export function indexForPartVariant(part: Part, variant?: string) {
  const spec = partAssetSpecs[part];
  const match = new RegExp(`^${spec.variantPrefix}-(\\d+)$`).exec(variant ?? '');
  return match ? clampAssetIndex(Number(match[1]), spec.count) : undefined;
}

function makeTiles(part: Part) {
  const spec = partAssetSpecs[part];
  return Array.from({ length: spec.count }, (_, index) => ({
    label: partLabels[part][index] ?? `${partNames[part]} ${String(index + 1).padStart(2, '0')}`,
    variant: `${spec.variantPrefix}-${index}`
  })) satisfies TileSpec[];
}

function clampAssetIndex(index: number, count: number) {
  return Number.isFinite(index) ? Math.min(Math.max(Math.trunc(index), 0), count - 1) : 0;
}

export const tileSpecs: Record<Part, readonly TileSpec[]> = {
  head: makeTiles('head'),
  arms: makeTiles('arms'),
  torso: makeTiles('torso'),
  legs: makeTiles('legs')
};
