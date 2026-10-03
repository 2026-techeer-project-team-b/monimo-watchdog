"""한 주기를 조립한다. 바깥과는 canary · notify 를 통해서만 말한다."""

import logging
import os
from typing import NamedTuple

import canary
import notify

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)
# Lambda 런타임이 루트 핸들러를 미리 달아 두어 위 줄이 아무 일도 하지 않는다. 평문 로그의
# 파이썬 런타임 기본 레벨은 WARN 이라, 직접 올리지 않으면 age_sec 이 CloudWatch 에 남지 않는다
logging.getLogger().setLevel(logging.INFO)


class Config(NamedTuple):
    shop_order_url: str
    api_server_url: str
    internal_token: str
    slack_webhook: str
    ping_url: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            shop_order_url=os.environ["SHOP_ORDER_URL"],
            api_server_url=os.environ["API_SERVER_URL"],
            internal_token=os.environ["MONIMO_INTERNAL_TOKEN"],
            slack_webhook=os.environ["SLACK_WEBHOOK"],
            ping_url=os.environ["PING_URL"],
        )


def lambda_handler(event, context):
    return run(Config.from_env())


def run(
    config: Config,
    send_order=canary.send_order,
    fetch_freshness=canary.fetch_freshness,
    post_slack=notify.post_slack,
    ping=notify.ping,
) -> dict:
    """결과를 돌려주되 던지지 않는다. 한 주기가 실패해도 다음 주기는 그대로 돈다."""
    try:
        return _cycle(config, send_order, fetch_freshness, post_slack)
    finally:
        # 판정이 어떻게 끝났든 보낸다. 안 보내면 Healthchecks 가 파수꾼이 죽은 것으로 본다
        _quietly("Healthchecks 핑", ping, config.ping_url)


def _cycle(config, send_order, fetch_freshness, post_slack) -> dict:
    try:
        traceparent = send_order(config.shop_order_url)
    except Exception:
        log.exception("카나리 주문 호출 실패")
        # 카나리를 못 넣었으니 조회하면 직전 주기 것이 잡혀 "정상"으로 오판한다
        _quietly("Slack", post_slack, config.slack_webhook, _ORDER_FAILED)
        return {"result": "ORDER_FAILED"}

    log.info("카나리 주문 전송 traceparent=%s", traceparent)

    try:
        freshness = fetch_freshness(config.api_server_url, config.internal_token)
    except Exception:
        log.exception("카나리 신선도 조회 실패")
        _quietly("Slack", post_slack, config.slack_webhook, _FRESHNESS_UNREACHABLE)
        return {"result": "FRESHNESS_UNREACHABLE"}

    if freshness.get("fresh"):
        log.info("카나리 정상 age_sec=%s", freshness.get("age_sec"))
        return {"result": "FRESH"}

    _quietly("Slack", post_slack, config.slack_webhook, _stale_text(freshness))
    return {"result": "STALE"}


def _quietly(what: str, call, *args) -> None:
    """실패를 로그로만 남긴다. 알림 · 핑이 터져도 나머지 주기는 끝까지 간다"""
    try:
        call(*args)
    except Exception:
        log.exception("%s 실패", what)


_ORDER_FAILED = ":rotating_light: 파수꾼 — 쇼핑몰 주문 API 에 카나리를 넣지 못했습니다. 신선도 조회는 건너뛰었습니다"
_FRESHNESS_UNREACHABLE = ":rotating_light: 파수꾼 — API 서버 신선도 조회에 실패했습니다. 파이프라인이 아니라 API 서버 쪽일 수 있습니다"


def _stale_text(freshness: dict) -> str:
    last_signal_at = freshness.get("last_signal_at") or "없음"
    return (
        ":rotating_light: 파수꾼 — 카나리가 끊겼습니다 "
        f"(마지막 신호 {last_signal_at}, {freshness.get('age_sec')}초 전 / 기준 {freshness.get('threshold_sec')}초)"
    )
