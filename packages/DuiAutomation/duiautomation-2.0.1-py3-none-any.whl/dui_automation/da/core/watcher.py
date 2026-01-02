from abc import abstractmethod, ABC


class Watcher(ABC):

    @abstractmethod
    def check_for_condition(self) -> bool:
        raise NotImplementedError
