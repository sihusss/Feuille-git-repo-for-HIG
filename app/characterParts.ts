export const parts = ['head', 'hair', 'upper', 'lower'] as const;

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

const ASSET_COUNT = 50;
export const CHARACTER_ASSET_BASE = '/assets/png_output';

export const partNames: Record<Part, string> = {
  head: '머리',
  hair: '머리카락',
  upper: '상의',
  lower: '하의'
};

export const partAssetSpecs: Record<Part, PartAssetSpec> = {
  head: {
    directory: 'heads',
    filePrefix: 'head_',
    fileExtension: 'png',
    variantPrefix: 'head',
    count: ASSET_COUNT
  },
  hair: {
    directory: 'hairs',
    filePrefix: 'hair_',
    fileExtension: 'png',
    variantPrefix: 'hair',
    count: ASSET_COUNT
  },
  upper: {
    directory: 'upper_bodies',
    filePrefix: 'upper_',
    fileExtension: 'png',
    variantPrefix: 'upper',
    count: ASSET_COUNT
  },
  lower: {
    directory: 'lower_bodies',
    filePrefix: 'lower_',
    fileExtension: 'png',
    variantPrefix: 'lower',
    count: ASSET_COUNT
  }
};

export function assetPathForPart(part: Part, index: number) {
  const spec = partAssetSpecs[part];
  const safeIndex = Number.isFinite(index) ? Math.min(Math.max(index, 0), spec.count - 1) : 0;
  return `${CHARACTER_ASSET_BASE}/${spec.directory}/${spec.filePrefix}${safeIndex}.${spec.fileExtension}`;
}

function makeTiles(part: Part) {
  const spec = partAssetSpecs[part];
  return Array.from({ length: spec.count }, (_, index) => ({
    label: `${partNames[part]} ${String(index + 1).padStart(2, '0')}`,
    variant: `${spec.variantPrefix}-${index}`
  })) satisfies TileSpec[];
}

export const tileSpecs: Record<Part, readonly TileSpec[]> = {
  head: makeTiles('head'),
  hair: makeTiles('hair'),
  upper: makeTiles('upper'),
  lower: makeTiles('lower')
};
