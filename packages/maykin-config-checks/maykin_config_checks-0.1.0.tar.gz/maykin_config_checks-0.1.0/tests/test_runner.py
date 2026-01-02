from maykin_config_checks import ErrorInfo, GenericHealthCheckResult, run_checks
from testapp.checks import CheckWithException, DummyCheck


def test_runner_with_checks_collector():
    results = run_checks(checks_collector=lambda: [DummyCheck()], include_success=False)

    assert len(list(results)) == 0


def test_runner_include_success():
    results = list(
        run_checks(checks_collector=lambda: [DummyCheck()], include_success=True)
    )

    assert len(results) == 1
    assert results[0].success


def test_runner_with_unexpected_exception():
    results = list(
        run_checks(
            checks_collector=lambda: [CheckWithException()], include_success=False
        )
    )

    assert len(results) == 1

    result = results[0]

    assert isinstance(result, GenericHealthCheckResult)
    assert not result.success
    assert hasattr(result, "extra") and isinstance(result.extra, ErrorInfo)
    assert "HELLO EXCEPTION" in result.extra.traceback
