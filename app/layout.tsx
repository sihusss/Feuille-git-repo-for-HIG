import './styles.css';

export const metadata = {
  applicationName: '인간 발명 대회',
  title: '인간 발명 대회',
  description: '휴대폰으로 인간을 만들고 랜덤 공개하는 모바일 웹 게임',
  icons: {
    icon: '/icon-192.png',
    apple: '/apple-icon.png'
  },
  appleWebApp: {
    capable: true,
    title: '인간 발명 대회',
    statusBarStyle: 'default'
  }
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#4c9a73'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
