from __future__ import annotations
from Copyable import Copyable
import copy
from Printable import Printable
import math

class Measure(Copyable, Printable):
    def __init__(self, ovalRef: Oval) -> None:
        self.ovalRef: Oval = ovalRef
        self.average_x: float = 0.0
        self.absoluteErr_x: float = 0.0
        self.average_y: float = 0.0
        self.absoluteErr_y: float = 0.0
        self.calc_average()
        self.calc_error()
    def calc_average(self) -> None:
        count = len(self.ovalRef.pixels)
        for pixel in self.ovalRef.pixels:
            self.average_x += pixel[0]
            self.average_y += pixel[1]
        self.average_x /= count
        self.average_y /= count
    def calc_error(self) -> None:
        if (self.average_x == 0 or self.average_y == 0):
            return 
        count = len(self.ovalRef.pixels)
        for pixel in self.ovalRef.pixels:
            self.absoluteErr_x += ((pixel[0] - self.average_x)**2)/count
            self.absoluteErr_y += ((pixel[1] - self.average_y)**2)/count
        self.absoluteErr_x = math.sqrt(self.absoluteErr_x)
        self.absoluteErr_y = math.sqrt(self.absoluteErr_y)
    
    def get_average_coords(self) -> list[float,float]:
        return [self.average_x, self.average_y]
    def __copy__(self) -> Measure:
        return self
    
    def __deepcopy__(self,memo) -> Measure:
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
  

class Oval(Copyable, Printable):
    pixels: list
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.pixels: list[int,int]  = []
        self.x_min: int = -1
        self.x_max: int = -1
        self.y_min: int = -1
        self.y_max: int = -1
        self.measureRef: Measure = None
    
    def set_pixels_collection(self,pixels_collection:list[list[int,int]]) -> None:
        self.pixels = copy.copy(pixels_collection)

    def update_measure_ref(self,measureRef: Measure) -> None:
        self.measureRef = measureRef

    def calculate_oval_bounding_box(self) -> None:
        for coords in self.pixels:
            if (self.x_min < 0 or coords[0] < self.x_min):
                self.x_min = coords[0]
            if (self.x_max < 0 or coords[0] > self.x_max):
                self.x_max = coords[0]
            if (self.y_min < 0 or coords[1] < self.y_min):
                self.y_min = coords[1]
            if (self.y_max < 0 or coords[1] > self.y_max):
                self.y_max = coords[1]
    def get_rectangle_bounding_box(self) -> tuple[int,int,int,int]:
        return (self.x_min, self.y_min, self.x_max, self.y_max)
    
    def __copy__(self) -> Oval:
        return self
    def __deepcopy__(self, memo) -> Oval:
        new_oval = Oval(self.id)
        new_oval.set_pixels_collection(self.pixels)
        new_oval.calculate_oval_bounding_box()
        new_oval.measureRef = self.measureRef
        return new_oval

    def __eq__(self, value: Oval) -> bool:
        temp_list_is_equals = set(self.pixels) == set(value.pixels)
        return self.measureRef == value.measureRef and self.x_max == value.x_max and self.x_min == value.x_min and self.y_min == value.y_min and self.y_max == value.y_max and temp_list_is_equals
  
    def __repr__(self) -> str:
        return f"Oval(pixels: {self.pixels}, x_min: {self.x_min}, x_max: {self.x_max}, y_min: {self.y_min}, y_max: {self.y_max})"
    
    def __str__(self) -> str:
        return f"""Oval id:{self.id} 
                 pixels number: {len(self.pixels)} 
                 width: {abs(self.x_max - self.x_min)} 
                 height: {abs(self.y_max - self.y_min)} 
                 coords: ({self.x_min},{self.y_min})"""
                