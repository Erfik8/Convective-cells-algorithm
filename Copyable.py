from abc import ABC, abstractclassmethod

class Copyable(ABC):
    @abstractclassmethod
    def __copy__(self):
        pass

    @abstractclassmethod
    def __deepcopy__(self, memo):
        pass
 