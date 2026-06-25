export const parts = ['head', 'arms', 'torso', 'legs'] as const;

export type Part = typeof parts[number];

export type TileSpec = {
  label: string;
  variant: string;
};

export type PartAssetSpec = {
  directory: string;
  filePrefix: string;
  fileExtension: string;
  variantPrefix: string;
  count: number;
};

export const CHARACTER_ASSET_BASE = '/assets/anime_parts';

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
    fileExtension: 'png',
    variantPrefix: 'head',
    count: 24
  },
  arms: {
    directory: 'arms',
    filePrefix: 'arms_',
    fileExtension: 'png',
    variantPrefix: 'arms',
    count: 24
  },
  torso: {
    directory: 'torsos',
    filePrefix: 'torso_',
    fileExtension: 'png',
    variantPrefix: 'torso',
    count: 24
  },
  legs: {
    directory: 'legs',
    filePrefix: 'legs_',
    fileExtension: 'png',
    variantPrefix: 'legs',
    count: 24
  }
};

const partLabels: Record<Part, readonly string[]> = {
  head: [
    '오렌지 골드 웨이브',
    '에스프레소 코일',
    '플래티넘 롱헤어',
    '애시 브라운 보브',
    '블랙 시스루뱅',
    '브라운 컬 헤일로',
    '하이탑 코일',
    '다크 웨이브 남성',
    '블랙 샤기 남성',
    '롱 블랙 웨이브',
    '오렌지 포니 웨이브',
    '에메랄드 코일',
    '실버 숏컷',
    '브라운 클립 보브',
    '블랙 롱 뱅',
    '숏 코일 헤어',
    '블루블랙 롱웨이브',
    '블랙 레이어드 남성',
    '블랙 웨이브 여성',
    '골드 링 코일',
    '실버 업스타일',
    '브라운 블런트 보브',
    '애시 블랙 뱅',
    '브라운 링 웨이브'
  ],
  arms: [
    '크림 카디건 소매',
    '머스터드 인사 팔',
    '블랙 데님 팔짱',
    '올리브 봄버 포즈',
    '화이트 셔츠 손바닥',
    '레드 트랙 팔짱',
    '차콜 코트 팔',
    '케이블 니트 손모음',
    '데님 재킷 인사',
    '파카 손모음',
    '레더 재킷 허리손',
    '베이지 트렌치 제스처',
    '크림 니트 한손',
    '블루 셔츠 오픈팜',
    '화이트 롤업 팔',
    '러스트 셔츠 팔',
    '차콜 재킷 손모음',
    '바시티 한손',
    '블랙 윈드브레이커',
    '플로럴 셔츠 팔',
    '오렌지 오버셔츠',
    '틸 봄버 팔',
    '블랙 후디 팔',
    '브라운 레더 팔짱'
  ],
  torso: [
    '크림 카디건 탱크',
    '머스터드 레이어드 티',
    '블랙 데님 재킷',
    '올리브 봄버',
    '화이트 버튼업 셔츠',
    '레드 트랙 재킷',
    '차콜 울 코트',
    '크림 케이블 카디건',
    '워시드 데님 재킷',
    '밀리터리 파카',
    '블랙 바이커 재킷',
    '그레이 오버코트',
    '베이지 트렌치',
    '크롭 니트 카디건',
    '페일 블루 옥스퍼드',
    '크림 리넨 셔츠',
    '카멜 스웨이드 재킷',
    '차콜 블레이저',
    '머스터드 바시티',
    '블랙 윈드브레이커',
    '플로럴 캠프 셔츠',
    '러스트 오버셔츠',
    '틸 봄버',
    '브라운 레더 재킷'
  ],
  legs: [
    '블랙 슬림 팬츠',
    '블루 체크 스커트',
    '데님 쇼츠 스니커즈',
    '블랙 쇼츠 부츠',
    '그레이 조거 팬츠',
    '블랙 플리츠 니삭스',
    '네이비 크롭 트라우저',
    '탄 카고 팬츠',
    '와이드 데님 팬츠',
    '블랙 러닝 쇼츠',
    '그레이 플리츠 스커트',
    '올리브 커프 팬츠',
    '데님 컷오프 쇼츠',
    '화이트 카고 팬츠',
    '블랙 미니스커트 망사',
    '라이트 블루 카고',
    '다크 데님 롤업',
    '블랙 드로스트링 팬츠',
    '레드 체크 스커트',
    '블랙 카고 부츠',
    '아이보리 플리츠 스커트',
    '블랙 와이드 팬츠',
    '라이트 리프드 데님',
    '네이비 쇼츠'
  ]
};

export function assetPathForPart(part: Part, index: number) {
  const spec = partAssetSpecs[part];
  const safeIndex = Number.isFinite(index) ? Math.min(Math.max(index, 0), spec.count - 1) : 0;
  return `${CHARACTER_ASSET_BASE}/${spec.directory}/${spec.filePrefix}${safeIndex}.${spec.fileExtension}`;
}

function makeTiles(part: Part) {
  const spec = partAssetSpecs[part];
  return Array.from({ length: spec.count }, (_, index) => ({
    label: partLabels[part][index] ?? `${partNames[part]} ${String(index + 1).padStart(2, '0')}`,
    variant: `${spec.variantPrefix}-${index}`
  })) satisfies TileSpec[];
}

export const tileSpecs: Record<Part, readonly TileSpec[]> = {
  head: makeTiles('head'),
  arms: makeTiles('arms'),
  torso: makeTiles('torso'),
  legs: makeTiles('legs')
};
