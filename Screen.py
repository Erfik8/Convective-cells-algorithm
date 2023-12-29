from __future__ import annotations
import copy
from Elements import Oval, Measure

class Screen:
    def __init__(self, path: str, timestamp: int) -> None:
        self.path: str = path
        self.oval_list: list[Oval] = []
        self.measures: list[Measure] = []
        self.timestamp: int = timestamp

    def set_Oval_list(self, oval_list: list[Oval]) -> None:
        self.oval_list = copy.deepcopy(oval_list)

    def set_Measure_list(self,measure_list: list[Measure]) -> None:
        self.measures = copy.deepcopy(measure_list)