from abc import abstractmethod


class Stream:
    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def stop(self):
        pass
