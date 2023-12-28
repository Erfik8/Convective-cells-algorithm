from Copyable import Copyable
import copy
from Printable import Printable
import math

class Oval(Copyable, Printable):
    pass

class Oval(Copyable, Printable):
    pixels: list
    def __init__(self, id: str) -> None:
        self.id = id
        self.pixels = []
        self.x_min = -1
        self.x_max = -1
        self.y_min = -1
        self.y_max = -1
        self.measureRef = None
    
    def set_pixels_collection(self,pixels_collection:list):
        self.pixels = copy.deepcopy(pixels_collection)

    def update_measure_ref(self,measureRef):
        self.measureRef = measureRef

    def calculate_oval_bounding_box(self):
        for coords in self.pixels:
            if (self.x_min < 0 or coords[0] < self.x_min):
                self.x_min = coords[0]
            if (self.x_max < 0 or coords[0] > self.x_max):
                self.x_max = coords[0]
            if (self.y_min < 0 or coords[1] < self.y_min):
                self.y_min = coords[1]
            if (self.y_max < 0 or coords[1] > self.y_max):
                self.y_max = coords[1]
    def get_rectangle_bounding_box(self):
        return (self.x_min, self.y_min, self.x_max, self.y_max)
    
    def __copy__(self):
        return self
    def __deepcopy__(self, memo):
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
                