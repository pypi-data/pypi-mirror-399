from io import StringIO

from django.core.management import call_command


def test_management_command():
    out = StringIO()
    call_command(
        "config_checks", checks_collector="testapp.checks.check_collector", stdout=out
    )

    assert "❌ Dummy fail: Everything is sad." == out.getvalue().strip("\n")


def test_management_command_with_success():
    out = StringIO()

    call_command(
        "config_checks",
        checks_collector="testapp.checks.check_collector",
        include_success=True,
        stdout=out,
    )

    assert "✅ Dummy\n❌ Dummy fail: Everything is sad." == out.getvalue().strip("\n")
