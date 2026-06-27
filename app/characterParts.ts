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
export const characterLayerOrder = ['legs', 'torso', 'arms', 'head'] as const satisfies readonly Part[];

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
    '이마 여드름과 짙은 눈썹 얼굴',
    '볼 여드름과 얇은 입술 얼굴',
    '여드름 패치를 붙인 큰 눈 얼굴',
    '피곤한 다크서클 걱정 얼굴',
    '주근깨가 있는 온화한 얼굴',
    '넓은 볼과 자신만만한 얼굴',
    '턱 여드름과 피곤한 눈매 얼굴',
    '점이 있는 차분한 얼굴',
    '여드름 흉터 느낌의 엄격한 얼굴',
    '주근깨와 둥근 볼 웃는 얼굴',
    '볼 여드름과 의심스러운 눈매',
    '치아 교정기가 보이는 놀란 얼굴',
    '두꺼운 눈썹과 이마 여드름 얼굴',
    '작은 입과 깨끗한 피부 얼굴',
    '여드름 패치와 소심한 얼굴',
    '한쪽 입꼬리와 볼 점 얼굴',
    '긴 코와 다크서클 냉정 얼굴',
    '넓은 얼굴과 볼 여드름 인상',
    '짧은 앞머리와 턱 여드름 얼굴',
    '반쯤 감긴 눈과 다크서클 얼굴',
    '작고 예민한 여드름 패치 얼굴',
    '넓은 미소와 교정기 얼굴',
    '직선 눈썹과 주근깨 얼굴',
    '활달한 눈과 이마 여드름 얼굴'
  ],
  arms: [
    '축 늘어진 긴소매 팔',
    '넓게 벌린 환영 팔',
    '가슴 앞에 교차한 팔',
    '허리에 얹은 당당한 팔',
    '한손 높이 흔드는 팔',
    '삿대질하는 날카로운 팔',
    '앞에서 손을 모은 팔',
    '팔짱 낀 방어적 팔',
    '어깨를 으쓱한 팔',
    '주머니에 찔러 넣은 팔',
    '설명하듯 벌린 팔',
    '몸을 가리는 경계 팔',
    '무겁게 내린 두꺼운 팔',
    '짧은소매 활짝 편 팔',
    '단정히 모은 긴 팔',
    '한쪽만 허리에 둔 팔',
    '소매 큰 손짓 팔',
    '앞을 찌르는 설명 팔',
    '맨팔로 벌린 팔',
    '작게 접은 경계 팔',
    '느슨한 팔짱 팔',
    '양손 주머니 팔',
    '차분히 내린 반소매 팔',
    '크게 설명하는 팔'
  ],
  torso: [
    '마른 흉곽이 보이는 티셔츠',
    '살집 있는 둥근 배 니트 조끼',
    '넓은 어깨와 큰 상체 블레이저',
    '평균 체형 짧은 후디',
    '탄탄하고 두꺼운 몸통 작업복',
    '키 큰 긴 코트 몸통',
    '평균 체형 앞치마 몸통',
    '살집 있는 넓은 원피스 몸통',
    '두꺼운 상체 줄무늬 스웨터',
    '넓은 어깨 유틸리티 조끼',
    '마른 허리 짧은 크롭 재킷',
    '키 큰 긴 튜닉 셔츠',
    '마른 목폴라 몸통',
    '살집 있는 풍성한 가디건',
    '넓은 어깨 각진 제복 재킷',
    '두꺼운 체형 헐렁한 후드',
    '평균 체형 페인트 작업복',
    '마른 몸을 덮는 긴 외투',
    '살집 있는 요리사 앞치마',
    '키 큰 주름 드레스 몸통',
    '둥근 배가 보이는 스웨터',
    '평균 체형 탐험가 조끼',
    '넓은 어깨 짧은 재킷',
    '두꺼운 체형 넉넉한 긴 셔츠'
  ],
  legs: [
    '작은 키 마른 일자 바지',
    '큰 키 평균 와이드 팬츠',
    '평균 키 튼튼한 반바지 하체',
    '작은 키 둥근 긴 치마',
    '평균 키 탄탄한 카고 바지',
    '작은 키 살집 있는 조거',
    '큰 키 마른 부츠컷',
    '평균 키 보통 체형 짧은 치마',
    '평균 키 살집 있는 넓은 바지',
    '작은 키 마른 데님 반바지',
    '평균 키 단단한 직선 바지',
    '큰 키 마른 긴 치마',
    '작은 키 둥근 카고 하체',
    '큰 키 마른 조거 하체',
    '평균 키 튼튼한 부츠컷',
    '작은 키 보통 플리츠 치마',
    '큰 키 평균 일자 바지',
    '작은 키 튼튼한 와이드 데님',
    '평균 키 살집 있는 운동 반바지',
    '평균 키 둥근 긴 치마',
    '큰 키 평균 카고 바지',
    '작은 키 보통 회색 조거',
    '큰 키 아주 마른 부츠컷',
    '평균 키 튼튼한 체크 치마'
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
