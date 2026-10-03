import re

import canary

TRACEPARENT = re.compile(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$")


def test_traceparent_는_w3c_모양이고_sampled_다():
    traceparent = canary.new_traceparent()

    assert TRACEPARENT.match(traceparent), traceparent
    trace_id = traceparent.split("-")[1]
    # 전부 0 이면 W3C 무효라 받는 쪽이 헤더를 버리고, 카나리가 흔적 없이 사라진다
    assert trace_id.strip("0")
