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
    '짙은 눈썹의 험상 얼굴',
    '얇은 입술의 비열한 얼굴',
    '큰 눈의 호기심 얼굴',
    '처진 눈썹의 걱정 얼굴',
    '반달 눈의 온화한 얼굴',
    '비웃는 듯한 자신만만 얼굴',
    '피곤한 눈매의 얼굴',
    '차분한 무표정 얼굴',
    '날카로운 턱의 엄격한 얼굴',
    '둥근 볼의 웃는 얼굴',
    '가느다란 눈매의 의심 얼굴',
    '놀란 입의 얼굴',
    '두꺼운 눈썹의 고집 얼굴',
    '작은 입의 조용한 얼굴',
    '축 처진 눈의 소심한 얼굴',
    '한쪽 입꼬리의 장난 얼굴',
    '긴 코의 냉정한 얼굴',
    '넓은 얼굴의 푸근한 인상',
    '짧은 앞머리의 까칠한 얼굴',
    '반쯤 감긴 졸린 얼굴',
    '작고 예민한 얼굴',
    '넓은 미소의 낙천 얼굴',
    '직선 눈썹의 냉담한 얼굴',
    '눈을 크게 뜬 활달 얼굴'
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
    '마른 기본 티셔츠',
    '둥근 배의 니트 조끼',
    '넓은 어깨 블레이저',
    '짧은 후디 상의',
    '작업복 멜빵 몸통',
    '긴 코트 몸통',
    '앞치마를 두른 몸통',
    '넓은 원피스 몸통',
    '두꺼운 줄무늬 스웨터',
    '주머니 많은 유틸리티 조끼',
    '짧은 크롭 재킷',
    '긴 튜닉 셔츠',
    '좁은 목폴라 몸통',
    '풍성한 가디건 몸통',
    '각진 제복 재킷',
    '헐렁한 후드 몸통',
    '페인트 묻은 작업복',
    '마른 긴 외투',
    '요리사 앞치마 몸통',
    '주름 많은 드레스 몸통',
    '둥근 배 스웨터',
    '탐험가 유틸리티 몸통',
    '각진 짧은 재킷',
    '넉넉한 긴 셔츠'
  ],
  legs: [
    '짧은 마른 일자 바지',
    '키 큰 와이드 팬츠',
    '튼튼한 반바지 하체',
    '둥근 실루엣 긴 치마',
    '주머니 큰 카고 바지',
    '헐렁한 조거 하체',
    '긴 마른 부츠컷',
    '활동적인 짧은 치마',
    '검은 넓은 바지',
    '짧은 데님 반바지',
    '단단한 직선 바지',
    '키 큰 긴 치마',
    '둥근 카고 하체',
    '마른 조거 하체',
    '넓은 종아리 부츠컷',
    '플리츠 치마 하체',
    '흰색 일자 바지',
    '두꺼운 와이드 데님',
    '운동 반바지 하체',
    '짙은 긴 치마',
    '높은 허리 카고 바지',
    '짧은 회색 조거',
    '날씬한 검정 부츠컷',
    '넓은 체크 치마'
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
