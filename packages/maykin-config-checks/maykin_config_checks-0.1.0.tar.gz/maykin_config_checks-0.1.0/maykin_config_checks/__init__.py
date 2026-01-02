import traceback
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from typing import Protocol

from django.utils.translation import gettext as _

JSONValue = dict[str, "JSONValue"] | list["JSONValue"] | str | int | float | bool | None

type Slug = str


class HealthCheckResult[T](Protocol):
    success: bool
    identifier: Slug
    """Identify from which health check this result comes from."""
    verbose_name: str
    message: str
    extra: T
    """Include additional information in the health check result."""

    def to_builtins(self) -> JSONValue:
        """Return a serialisable object."""
        ...


class HealthCheck[T](Protocol):
    identifier: Slug
    verbose_name: str

    def __call__(self) -> HealthCheckResult[T]: ...


type HealthCheckCollector = Callable[[], Iterable[HealthCheck]]


@dataclass
class ErrorInfo:
    traceback: str


@dataclass
class GenericHealthCheckResult:
    success: bool
    identifier: Slug
    verbose_name: str
    message: str
    extra: ErrorInfo | None = None

    def to_builtins(self) -> JSONValue:
        return asdict(self)


def run_checks(
    checks_collector: HealthCheckCollector, include_success: bool
) -> Iterable[HealthCheckResult]:
    results = []
    for check in checks_collector():
        try:
            result = check()
        except Exception:
            result = GenericHealthCheckResult(
                identifier=check.identifier,
                verbose_name=check.verbose_name,
                success=False,
                message=_("Something unexpected went wrong."),
                extra=ErrorInfo(
                    traceback=traceback.format_exc(),
                ),
            )
        if not result.success or (result.success and include_success):
            results.append(result)
    return results
