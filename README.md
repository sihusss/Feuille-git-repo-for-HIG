# 인간 발명 대회

휴대폰 여러 대로 같은 방에 접속해서 인간을 만들고, 각 휴대폰마다 방 안의 인간 하나를 중복 없이 랜덤 공개하는 모바일 웹 게임입니다.

## 기술 구성

- Next.js App Router
- React
- TypeScript
- Firebase Realtime Database 선택 저장소
- Vercel 배포

## 로컬 실행

```bash
npm install
npm run dev
```

브라우저에서 `http://localhost:3000`에 접속합니다.

같은 와이파이의 휴대폰으로 테스트하려면 PC의 로컬 IP를 사용하세요.
예: `http://192.168.0.10:3000`

## 게임 흐름

- 선 플레이어가 6자리 참가 코드 방 생성
- 참가자는 코드 또는 초대 링크로 입장
- 선 플레이어가 모두 접속 완료 처리
- 국가명 입력 후 게임 시작
- 라운드마다 신체부위 순서 랜덤 제공
- 각 신체부위마다 4개 랜덤 타일 중 하나 선택
- 머리, 머리카락, 상의, 하의 선택 후 인간 완성
- 모든 플레이어가 완성하면 인간 공개 단계 진입
- 각 휴대폰에 방 안의 인간 1개를 중복 없이 랜덤 공개
- 참여한 플레이어 수 x 2라운드부터 `게임 끝` 버튼 강조

## 저장소

Firebase Realtime Database 환경 변수가 있으면 방 상태를 Firebase에 저장합니다.
환경 변수가 없으면 서버 메모리 저장소로 동작하므로 개발 서버를 재시작하거나 서버리스 인스턴스가 바뀌면 방이 사라질 수 있습니다.

필요한 환경 변수:

```text
FIREBASE_DATABASE_URL
FIREBASE_SERVICE_ACCOUNT_KEY
```

`FIREBASE_SERVICE_ACCOUNT_KEY`는 서비스 계정 JSON 문자열 또는 base64 인코딩된 JSON 문자열을 사용할 수 있습니다. 대신 아래처럼 나눠서 넣어도 됩니다.

```text
FIREBASE_PROJECT_ID
FIREBASE_CLIENT_EMAIL
FIREBASE_PRIVATE_KEY
```

로컬의 `.env*`, `tokens/`, `firebase-rtdb-secrets.txt`는 Git/Vercel 배포 대상에서 제외합니다.

## 검증

```bash
npm run lint
npm run build
```

`npm run lint`는 `next typegen` 후 TypeScript 검사를 실행합니다.

## 배포

현재 프로덕션 배포 주소:

```text
https://human-invention-game.vercel.app
```

Vercel 프로젝트는 로컬 `.vercel/project.json`에 연결되어 있습니다. 이 폴더는 Git에 올리지 않습니다.

프로덕션 배포:

```bash
npm run deploy
```

Preview 배포:

```bash
npm run deploy:preview
```

배포 스크립트는 배포 전에 `npm run lint`와 `npm run build`를 먼저 실행합니다.

## GitHub 동기화

원격 저장소:

```text
https://github.com/sihusss/Feuille-git-repo-for-HIG
```

수정 후 기본 동기화 흐름:

```bash
git status
git add .
git commit -m "Describe changes"
git push origin main
```
