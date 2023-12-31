from __future__ import annotations
from Entitie import Entitie
from Elements import Measure
import math

class ProbabilityDensityDistribution:
    def __init__(self,entitie: Entitie, measure: Measure) -> None:
        self.measure: Measure = measure
        self.entitie: Entitie = entitie
        self.value: float = self.calc()
    
    def calc(self) -> float:
        mean_x, mean_y, err_x, err_y = self.entitie.predicted_position()
        measure_x = self.measure.average_x
        measure_y = self.measure.average_y
        measure_err_x = self.measure.absoluteErr_x
        measure_err_y = self.measure.absoluteErr_y
        absolute_err_x = 0.0
        absolute_err_y = 0.0
        absolute_err_x = abs(measure_err_x - err_x)/max(measure_err_x,err_x)
        absolute_err_y = abs(measure_err_y - err_y)/max(measure_err_y,err_y)
        shape_probability = (1-absolute_err_x)*(1-absolute_err_y)**2
        return_val = shape_probability
        if(err_x != 0.0):
            return_val *= math.exp((-((measure_x - mean_x)**2))/(2*5.0**4))
        if(err_y != 0.0):
            return_val *= math.exp((-((measure_y - mean_y)**2))/(2*5.0**4))
        return return_val