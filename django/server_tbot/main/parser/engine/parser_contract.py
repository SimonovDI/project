from abc import ABC, abstractmethod


class ParserContract(ABC):

    @abstractmethod
    def parse(self):
        pass


