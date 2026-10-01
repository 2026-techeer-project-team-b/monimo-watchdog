# monimo-watchdog

파수꾼: 우리 스택 바깥에서 카나리 데이터로 파이프라인이 살아 있는지 확인하는 Lambda

- 기술: Python · Terraform · AWS Lambda · EventBridge Scheduler
- 상태: 카나리 한 주기 구현 완료. 배포(Terraform · OIDC)는 아직

## 폴더 구성

| 폴더 | 하는 일 |
|---|---|
| `src/handler.py` | 한 주기를 조립한다. 바깥과는 아래 둘을 통해서만 말한다 |
| `src/canary.py` | `traceparent` 생성 · 쇼핑몰 주문 호출 · 신선도 조회 |
| `src/notify.py` | Slack 웹훅 · Healthchecks.io 핑 |
| `tests/` | pytest. 네트워크를 타지 않는다 |
| `infra/` | Terraform: Lambda · EventBridge Scheduler |

표준 라이브러리만 쓴다. `src/` 내용물을 zip 으로 묶어 올리는 것이 배포의 전부다.

## 한 주기

1. `traceparent`(`00-<32hex>-<16hex>-01`) + `tracestate: monimon=canary` 를 붙여 쇼핑몰 주문 API 에 가짜 주문 1건
2. 바로 `GET /api/v1/internal/canary/freshness?service_name=shop-order` (`X-Internal-Token`)
3. `fresh` 가 false 면 전용 Slack 웹훅
4. 무엇으로 끝났든 Healthchecks.io 핑

**기다리지 않는다.** 2번에서 보이는 것은 방금 쏜 카나리가 아니라 직전 주기(60초 전)에 쏜 것이다. 내 것이 도착할 때까지 기다리면 Lambda 가 30~60초를 붙잡고 있어야 해서 1분 주기에 상주 서버와 다를 게 없어진다.

**판정하지 않는다.** `fresh` 는 API 서버가 낸다. 기준값(`MONIMO_CANARY_THRESHOLD_SEC`, 180초)을 조일 때 파수꾼을 다시 배포하지 않으려고.

## 로컬 실행

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest                                  # 네트워크 없이

cp .env.example .env                    # 값을 채운 뒤
set -a && . ./.env && set +a
PYTHONPATH=src python -c 'from handler import Config, run; print(run(Config.from_env()))'
```

## 환경변수

실제 값은 레포에 올리지 않는다. `.env.example` 에 이름만 적는다.

| 이름 | 설명 |
|---|---|
| `SHOP_ORDER_URL` | 카나리가 호출할 쇼핑몰 주문 API |
| `API_SERVER_URL` | 카나리 신선도를 조회할 API 서버 |
| `PING_URL` | Healthchecks.io 핑 주소 (Dead Man's Switch) |
| `MONIMO_INTERNAL_TOKEN` | 내부 문 출입증. API 서버의 같은 이름 값과 맞춘다 |
| `SLACK_WEBHOOK` | 파수꾼 전용 슬랙 웹훅 (관제 스택과 별도 채널) |

운영(Lambda)에서는 `infra/` 의 Terraform 이 같은 이름으로 넣는다.

## 관련 문서

- [설계 문서 (결정 기록 원본)](https://github.com/2026-techeer-project-team-b/monimo-backend/tree/main/docs/design): monimo-backend 레포의 `docs/design/`
- [레포별 파일 구성](https://app.notion.com/p/3e1d7d6851ff80a8a110e8aea0b5783b)
- [깃허브 레포지토리 규칙](https://app.notion.com/p/3dcd7d6851ff8000b795f1cc609124e6)

## 기여 규칙

- `main` 직접 push 금지, PR로만 머지
- 브랜치: `feat/<이슈번호>-<설명>` · `fix/<이슈번호>-<설명>` · `chore/<설명>`
- 커밋: `<타입>: <요약> (#이슈)` 한 줄 (타입: feat · fix · docs · chore · refactor · test · ci). 이 레포는 모듈이 하나라 범위를 붙이지 않는다
