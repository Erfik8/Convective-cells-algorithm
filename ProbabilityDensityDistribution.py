from Entitie import Entitie
import math

class ProbabilityDensityDistribution:
    def __init__(self,entitie: Entitie, x: int,y: int) -> None:
        self.x = x
        self.y = y
        self.entitie = entitie
        self.value = self.calc()
    
    def calc(self) -> float:
        mean_x, mean_y, err_x, err_y = self.entitie.predicted_position()
        # print(mean_x, mean_y, err_x, err_y)
        return math.exp((-((self.x - mean_x)**2))/(2*err_x**5))*math.exp((-((self.y - mean_y)**2))/(2*err_y**5))
