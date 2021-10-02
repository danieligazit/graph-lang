from abc import abstractmethod, ABC


class Document(ABC):
    @classmethod
    @abstractmethod
    def _get_collection(cls):
        pass


class Edge(Document):
    pass
