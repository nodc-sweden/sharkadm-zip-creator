
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import StrEnum, auto


class States(StrEnum):
    TEST = auto()
    PROD = auto()


@dataclass
class State(ABC):
    app: "AppState" = field(repr=False)
    visible: tuple[str, ...] = ()
    state: States = None
    test_text: str = "Testtext utan state"
    app_title: str = "Zip archive creator"
    log_file_name: str = "zip_creator_log.txt"

    @abstractmethod
    def set_to_prod(self) -> None: ...

    @abstractmethod
    def set_to_test(self) -> None: ...

    def is_visible(self, name: str) -> bool:
        return name in self.visible


@dataclass
class ProdState(State):
    visible: tuple[str, ...] = ("single_zip", )
    state: States = States.PROD
    test_text: str = "Testtext för PROD"
    app_title: str = "Zip archive creator (prod)"
    log_file_name: str = "zip_creator_log_prod.txt"

    def set_to_prod(self) -> None:
        print("Already in prod")

    def set_to_test(self) -> None:
        self.app.set_state(TestState(self.app))


@dataclass
class TestState(State):
    visible: tuple[str, ...] = ("temp",)
    state: States = States.TEST
    test_text: str = "Testtext för TEST"
    app_title: str = "Zip archive creator (test)"
    log_file_name: str = "zip_creator_log_test.txt"

    def set_to_prod(self) -> None:
        self.app.set_state(ProdState(self.app))

    def set_to_test(self) -> None:
        print("Already in test")


class AppState:
    def __init__(self):
        self.state: State = ProdState(self)

    def set_state(self, state: State):
        self.state = state

    def set_to_prod(self) -> None:
        self.state.set_to_prod()

    def set_to_test(self) -> None:
        self.state.set_to_test()

