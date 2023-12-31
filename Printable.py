from abc import ABC, abstractclassmethod
class Printable:
    @abstractclassmethod
    def __str__(self) -> str:
        pass
    def __repr__(self) -> str:
        pass