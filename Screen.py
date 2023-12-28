import copy

class Screen:
    def __init__(self, path: str, timestamp: int) -> None:
        self.path = path
        self.oval_list = []
        self.measures = []
        self.timestamp = timestamp

    def set_Oval_list(self, oval_list: list):
        self.oval_list = copy.deepcopy(oval_list)