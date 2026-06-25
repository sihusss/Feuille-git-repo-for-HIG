import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: '인간 발명 대회',
    short_name: '인간 발명',
    description: '휴대폰으로 인간을 만들고 랜덤 공개하는 모바일 웹 게임',
    start_url: '/',
    display: 'standalone',
    background_color: '#d7e7d2',
    theme_color: '#4c9a73',
    icons: [
      {
        src: '/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'any'
      },
      {
        src: '/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'maskable'
      }
    ]
  };
}
