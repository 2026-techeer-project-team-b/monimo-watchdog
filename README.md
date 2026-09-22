# monimo-watchdog

파수꾼: 우리 스택 바깥에서 카나리 데이터로 파이프라인이 살아 있는지 확인하는 Lambda

- 기술: Python · Terraform · AWS Lambda · EventBridge Scheduler
- 상태: 뼈대만 있음 (개발환경 세팅 중)

## 폴더 구성

| 폴더 | 하는 일 |
|---|---|
| `src/` | 카나리 한 흐름 (주문 API 호출 → API 서버 조회 → 판정) |
| `infra/` | Terraform: Lambda · EventBridge Scheduler |

## 로컬 실행

준비 중

## 환경변수

실제 값은 레포에 올리지 않는다. `.env.example` 에 이름만 적는다.

| 이름 | 설명 |
|---|---|
| `SHOP_ORDER_URL` | 카나리가 호출할 쇼핑몰 주문 API |
| `API_SERVER_URL` | 카나리 신선도를 조회할 API 서버 |
| `PING_URL` | Healthchecks.io 핑 주소 (Dead Man's Switch) |
| `SLACK_WEBHOOK` | 파수꾼 전용 슬랙 웹훅 (관제 스택과 별도 채널) |
| `CANARY_WAIT_SECONDS` | 주문 호출 뒤 조회까지 기다리는 시간(초), 기본 30 |

운영(Lambda)에서는 `infra/` 의 Terraform 이 같은 이름으로 넣는다.

## 포트

| 서비스 | 포트 |
|---|---|
| (준비 중) | |

## 관련 문서

- [설계 문서 (결정 기록 원본)](https://github.com/2026-techeer-project-team-b/monimo-backend/tree/main/docs/design): monimo-backend 레포의 `docs/design/`
- [레포별 파일 구성](https://app.notion.com/p/3e1d7d6851ff80a8a110e8aea0b5783b)
- [깃허브 레포지토리 규칙](https://app.notion.com/p/3dcd7d6851ff8000b795f1cc609124e6)

## 기여 규칙

- `main` 직접 push 금지, PR로만 머지
- 브랜치: `feat/<이슈번호>-<설명>` · `fix/<이슈번호>-<설명>` · `chore/<설명>`
- 커밋: `<타입>(<범위>): <요약>` (타입: feat · fix · docs · chore · refactor · test)
