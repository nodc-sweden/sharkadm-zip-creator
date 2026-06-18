from enum import StrEnum, auto


class Events(StrEnum):
    CHANGE_STATE = auto()
    CHANGE_SOURCE_TYPE = auto()
    CHANGE_SINGLE_DATA_SOURCE = auto()
    RUN_EXPORTER = auto()
    SHOW_DIALOG = auto()
    SHOW_INFO = auto()
    RESET_PROGRESS = auto()
    DISABLE = auto()
    ENABLE = auto()


_subscribers = dict((str(ev), dict()) for ev in Events)


class EventNotFound(Exception):
    pass


def get_events() -> list[str]:
    return sorted(_subscribers)


def subscribe(event: str | Events, func, prio: int = 50) -> None:
    event = str(event)
    if event not in _subscribers:
        raise EventNotFound(event)
    _subscribers[event].setdefault(prio, [])
    if func in _subscribers[event][prio]:
        return
    _subscribers[event][prio].append(func)


def post_event(event: str | Events, data: dict | str | None = None) -> None:
    if event not in _subscribers:
        raise EventNotFound(event)

    for prio in sorted(_subscribers[event]):
        for func in _subscribers[event][prio]:
            func(data)
