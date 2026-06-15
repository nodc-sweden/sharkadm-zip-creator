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
    # print(f"subscribe: {event=}")
    # print(f"subscribe: {_subscribers[event]=}")
    # print(f"subscribe: {len(_subscribers[event])=}")


def post_event(event: str | Events, data: dict | str) -> None:
    # event = str(event)
    # if type(data) is str:
    #     data = dict(msg=data)
    if event not in _subscribers:
        raise EventNotFound(event)
    # print()
    # print(f"post_event: {data=}")
    # print(f"post_event: {event=}")
    # print(f"post_event: {_subscribers[event]=}")
    # print(f"post_event: {len(_subscribers[event])=}")
    # print(f"post_event: {id(_subscribers)=}")
    # print()
    # print(f"post_event: {_subscribers=}")
    # print("#"*100)

    for prio in sorted(_subscribers[event]):
        for func in _subscribers[event][prio]:
            func(data)

# def clear_subscribers() -> None:
#     _subscribers = dict((str(ev), dict()) for ev in Events)
