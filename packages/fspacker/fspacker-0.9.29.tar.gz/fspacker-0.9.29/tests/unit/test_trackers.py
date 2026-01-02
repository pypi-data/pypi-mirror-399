import pytest

from fspacker.logger import logger
from fspacker.settings import settings
from fspacker.trackers import perf_tracker
from fspacker.trackers import PerformanceTracker


def test_perf_tracker(caplog: pytest.LogCaptureFixture) -> None:
    logger.set_debug_mode(debug_mode=True)

    @perf_tracker
    def fabonacci(n: int) -> int:
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return b

    assert fabonacci(10) == 144  # noqa: PLR2004
    PerformanceTracker.finalize()

    assert "性能统计" in caplog.text
    assert "总运行时间:" in caplog.text


def test_perf_tracker_no_debug(caplog: pytest.LogCaptureFixture) -> None:
    settings.mode.debug = False

    @perf_tracker
    def fabonacci(n: int) -> int:
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return b

    assert fabonacci(10) == 144  # noqa: PLR2004
    assert "总运行时间:" not in caplog.text
