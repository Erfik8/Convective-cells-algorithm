from Copyable import Copyable
from Oval import Oval
import math
from Printable import Printable

class Measure(Copyable):
    def __init__(self, ovalRef: Oval) -> None:
        self.ovalRef = ovalRef
        self.average_x = 0
        self.absoluteErr_x = 0
        self.average_y = 0
        self.absoluteErr_y = 0
        self.calc_average()
        self.calc_error()
    def calc_average(self):
        count = len(self.ovalRef.pixels)
        for pixel in self.ovalRef.pixels:
            self.average_x += pixel[0]
            self.average_y += pixel[1]
        self.average_x /= count
        self.average_y /= count
    def calc_error(self):
        if (self.average_x == 0 or self.average_y == 0):
            return 
        count = len(self.ovalRef.pixels)
        for pixel in self.ovalRef.pixels:
            self.absoluteErr_x += ((pixel[0] - self.average_x)**2)/count
            self.absoluteErr_y += ((pixel[1] - self.average_y)**2)/count
        self.absoluteErr_x = math.sqrt(self.absoluteErr_x)
        self.absoluteErr_y = math.sqrt(self.absoluteErr_y)
    
    def __copy__(self):
        return self
    
    def __deepcopy__(self,memo):
        new_measure = Measure(self.ovalRef)
        new_measure.average_x = self.average_x
        new_measure.average_y = self.average_y
        new_measure.absoluteErr_x = self.absoluteErr_x
        new_measure.absoluteErr_y = self.absoluteErr_y
        return new_measure
    
    def __repr__(self) -> str:
        return f"Measure(average_x: {self.average_x}, average_y: {self.average_y}, absoluteErr_x: {self.absoluteErr_x}, absoluteErr_y: {self.absoluteErr_y})"
    
    def __str__(self) -> str:
        return f"""Measure id: {self.ovalRef.id} 
                 coords: ({self.average_x},{self.average_y})"""
  