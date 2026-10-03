from handler import Config, run

CONFIG = Config(
    shop_order_url="http://shop/api/orders",
    api_server_url="http://api",
    internal_token="token",
    slack_webhook="http://slack",
    ping_url="http://ping",
)

STALE = {"last_signal_at": "2026-10-01T00:00:00Z", "age_sec": 900, "threshold_sec": 180, "fresh": False}


class Spy:
    """부른 횟수만 센다. 네트워크를 타지 않는다"""

    def __init__(self, result=None, error=None):
        self.calls = []
        self._result = result
        self._error = error

    def __call__(self, *args):
        self.calls.append(args)
        if self._error:
            raise self._error
        return self._result


def test_카나리가_끊기면_slack_을_부른다():
    slack = Spy()

    result = run(CONFIG, send_order=Spy("tp"), fetch_freshness=Spy(STALE), post_slack=slack, ping=Spy())

    assert result == {"result": "STALE"}
    assert "900초 전" in slack.calls[0][1]


def test_조회가_터져도_핑은_나간다():
    heartbeat = Spy()

    result = run(
        CONFIG,
        send_order=Spy("tp"),
        fetch_freshness=Spy(error=TimeoutError()),
        post_slack=Spy(),
        ping=heartbeat,
    )

    assert result == {"result": "FRESHNESS_UNREACHABLE"}
    assert heartbeat.calls == [(CONFIG.ping_url,)]


def test_주문이_실패하면_조회를_건너뛴다():
    freshness = Spy(STALE)

    result = run(
        CONFIG,
        send_order=Spy(error=ConnectionError()),
        fetch_freshness=freshness,
        post_slack=Spy(),
        ping=Spy(),
    )

    # 조회했으면 직전 주기 카나리가 잡혀 "정상" 으로 오판했을 자리다
    assert result == {"result": "ORDER_FAILED"}
    assert freshness.calls == []
