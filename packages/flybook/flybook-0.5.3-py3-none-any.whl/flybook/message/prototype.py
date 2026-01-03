from abc import ABC, abstractproperty, abstractmethod


class Message(ABC):
    @abstractproperty
    def data(self):
        raise NotImplementedError()
