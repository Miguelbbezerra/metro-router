"""Domain errors. The CLI turns any ``MetroRouterError`` into a clean message."""

from collections.abc import Sequence


class MetroRouterError(Exception):
    """Base class for every expected, user-facing error."""


class NetworkFileError(MetroRouterError):
    """The network definition file is missing, malformed or inconsistent."""


class StationNotFoundError(MetroRouterError):
    """No station matches the name the user typed."""

    def __init__(self, query: str, suggestions: Sequence[str] = ()) -> None:
        self.query = query
        self.suggestions = list(suggestions)
        message = f"Unknown station {query!r}."
        if self.suggestions:
            message += f" Did you mean: {', '.join(self.suggestions)}?"
        super().__init__(message)


class NoRouteError(MetroRouterError):
    """The two stations are not connected."""

    def __init__(self, origin: str, destination: str) -> None:
        super().__init__(f"No route between {origin!r} and {destination!r}.")
