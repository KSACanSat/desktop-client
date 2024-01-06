from abc import abstractmethod


class Stream:
    @property
    def get_type(self):
        return "Please specify"

    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def stop(self):
        pass
