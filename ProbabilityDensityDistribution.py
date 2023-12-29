from __future__ import annotations
from Entitie import Entitie
import math

class ProbabilityDensityDistribution:
    def __init__(self,entitie: Entitie, x: float,y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.entitie: Entitie = entitie
        self.value: float = self.calc()
    
    def calc(self) -> float:
        mean_x, mean_y, err_x, err_y = self.entitie.predicted_position()
        # print(mean_x, mean_y, err_x, err_y)
        #return math.exp((-((self.x - mean_x)**2))/(2*math**5))*math.exp((-((self.y - mean_y)**2))/(2*err_y**5))
        return_val = 1
        if(err_x != 0.0):
            return_val *= math.exp((-((self.x - mean_x)**2))/(2*err_x**5))
        if(err_y != 0.0):
            return_val *= math.exp((-((self.y - mean_y)**2))/(2*err_y**5))
        return return_val