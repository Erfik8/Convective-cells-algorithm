import urllib
import json
import xmltodict
import random
import tkinter as tk
from tkinter import ttk
import math
import copy
import tkcap
import time

class Singleton(object):
    _instance = None

    def __new__(singleton):
        if singleton._instance is None:
            print('Creating the object')
            singleton._instance = super(Singleton, singleton).__new__(singleton)
            # Put any initialization here.
        return singleton._instance
    
    def getInstance(singleton):
        return singleton._instance
    
class Constants(Singleton):
    def __init__(self) -> None:
        super().__init__()
        self._MAX_VELOCITY = 1
        self._AREA_WIDTH = 80
        self._AREA_HEIGHT = 45
        self._AREA_OFFSET_X = 5
        self._AREA_OFFSET_Y = 5
        self._SCALE_FACTOR = 20
        self._POPULATION_COUNT = 6
        self._FRAMES_PER_SEC = 40
        self._NEW_POPULATION_FACTOR = 0.08
        self._START_POPULATION = 6
        self._INFECTION_PROBAILLITY = 0.1
        self._TIME_TO_INFECT = 1
        self._INFECTION_RADIUS = 2
        self._TIME_TO_RESISTANCE = 15


_constants = Constants()



class IPolar2D:
    def getAngle(self) -> float:
        pass
    def abs(self) -> float:
        pass

class IVector:
    def abs(self) -> float:
        pass
    def cdot(self,IVectorObj) -> float:
        pass
    def getComponents(self):
        pass

class Vector2D(IVector):
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
    def abs(self) -> float:
        return (self.x**2 + self.y**2)**(1/2)
    def cdot(self,IVectorObj) -> float:
        return self.x*IVectorObj.getComponents()[0] + self.y*IVectorObj.getComponents()[1]
    def getComponents(self):
        return [self.x,self.y]

class Polar2DAdapter(IPolar2D,IVector):
    def __init__(self,vector2DObj) -> None:
        self.srcVector2D = vector2DObj
    def abs(self) -> float:
        return self.srcVector2D.abs()
    def cdot(self,IVectorObj) -> float:
        return self.srcVector2D.cdot(IVectorObj)
    def getComponents(self):
        return self.srcVector2D.getComponents()
    def getAngle(self):
        return math.asin(self.srcVector2D.getComponents()[1]/self.srcVector2D.abs())
    
class Polar2DInheritance(Vector2D):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)
    def getAngle(self):
        return math.asin(self.y/self.abs())

def addVectors(vec1: Vector2D, vec2: Vector2D):
    return Vector2D(vec1.getComponents()[0] + vec2.getComponents()[0],
                    vec1.getComponents()[1] + vec2.getComponents()[1])



class Person():
    location: Vector2D
    velocity: Vector2D
    point_object_ID: int
    area_lowering_factor: float
    is_resistant: bool
    is_health: bool
    has_symptoms: bool
    infection_contact: int
    time_to_recover: int
    def __init__(self,pos_x,pos_y,vel_x,vel_y,point_object_id = 0) -> None:
        self.location = Vector2D(pos_x,pos_y)
        self.velocity = Vector2D(vel_x,vel_y)
        self.point_object_ID = point_object_id
        self.normalize_velocity(_constants._MAX_VELOCITY)
        self.area_lowering_factor = 0.5
        self.is_resistant = False
        self.is_health = bool(round(random.random()))
        self.has_symptoms = bool(round(random.random()))
        self.infection_contact = 0
        self.time_to_recover = 0
    
    def normalize_velocity(self,max_velocity) -> None:
        temp_velocity_value = self.velocity.abs()
        shrink_factor = max_velocity/temp_velocity_value
        self.velocity.x = self.velocity.x*shrink_factor
        self.velocity.y = self.velocity.y*shrink_factor
    def new_velocity(self,max_velocity) -> None:
        pass
    def update_point_object_id(self,point_object_ID):
        self.point_object_ID = point_object_ID
    def update_position(self):
        temp_velocity = copy.deepcopy(self.velocity)
        temp_velocity.x/=_constants._SCALE_FACTOR
        temp_velocity.y/=_constants._SCALE_FACTOR
        self.location = addVectors(self.location,temp_velocity)

    def update_infection_contact(self,time_of_contatct: int):
        self.infection_contact += time_of_contatct

    def update_time_to_recover(self):
        if(self.time_to_recover <= _constants._TIME_TO_RESISTANCE):
            if (self.is_resistant == False and self.is_health == False):
                self.time_to_recover += 1
                if(self.time_to_recover > _constants._TIME_TO_RESISTANCE):
                    self.is_resistant = True
                    self.is_health = True


class Tkwindow():
    def __init__(self, title = "Sample program") -> None:
        self.root = tk.Tk()
        self.root.title(title)
        self.canvas = tk.Canvas(self.root, width=_constants._AREA_WIDTH*_constants._SCALE_FACTOR, height=_constants._AREA_HEIGHT*_constants._SCALE_FACTOR)
        self.canvas.pack()
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(side=tk.RIGHT, padx=10)
        #self.root.bind('<Key>',self.on_key)
    def run(self):
        self.root.mainloop()
    def on_key(self,event,config_string):
        if event.char == 's':
            self.text_information.config(state=tk.NORMAL)
            self.text_information.insert(tk.END, config_string)
            self.text_information.config(state=tk.DISABLED)
        elif event.char == 'r':
            current_content = self.text_information.get("1.0", tk.END)
            last_newline_index = current_content.rfind('\n')  # Find the last newline character
            print(self.text_information.index("end") + '- 1 lines',' ',tk.END)
            self.text_information.config(state=tk.NORMAL)
            self.text_information.delete(self.text_information.index("end") + ' - 1 lines', tk.END)  # Delete the entire last line
            self.text_information.config(state=tk.DISABLED)
        
    def update_person(self, person: Person):
        self.canvas.move(person.point_object_ID,
                         person.velocity.getComponents()[0],person.velocity.getComponents()[1])
        new_coords = list(self.canvas.coords(person.point_object_ID))
        #new_coords[2] += (-0.5)+random.random()
        #new_coords[3] += (-0.5)+random.random()
        self.canvas.coords(person.point_object_ID,*new_coords)
        self.update_person_infection(person)
    def update_person_infection(self, person: Person):
        if(person.is_health == True and person.is_resistant == False):
            self.canvas.itemconfigure(person.point_object_ID,fill='blue')
        elif(person.is_health == False and person.is_resistant == False and person.has_symptoms == False):
            self.canvas.itemconfigure(person.point_object_ID,fill='orange')
        elif(person.is_health == False and person.is_resistant == False and person.has_symptoms == True):
            self.canvas.itemconfigure(person.point_object_ID,fill='red')
        elif(person.is_resistant == True):            
            self.canvas.itemconfigure(person.point_object_ID,fill='green')
    def generate_person_oval(self, person: Person) -> int:
        x,y = person.location.getComponents()
        return self.canvas.create_oval(x * _constants._SCALE_FACTOR,
                                        y * _constants._SCALE_FACTOR,
                                          x * _constants._SCALE_FACTOR + 14 + random.random()*10,
                                            y * _constants._SCALE_FACTOR + 14 + random.random()*10,
                                              fill="blue")
    def remove_person_oval(self, person: Person):
        self.canvas.delete(person.point_object_ID)

    def get_person_oval_coords(self,person: Person):
        return list(self.canvas.coords(person.point_object_ID))
    

class Simulation():
    area_x: float
    area_y: float
    area_start_x: float 
    area_start_y: float
    population: list
    tkwindow: Tkwindow
    simulation_time: int

    def __init__(self,n,m,title,pos_x = 0, pos_y = 0) -> None:
        self.area_x = n
        self.area_y = m
        self.area_start_x = pos_x
        self.area_start_y = pos_y
        self.population = list()
        self.tkwindow = Tkwindow(title)
        self.simulation_time = 0

    def generate_list(self,n):
        for a in range(0,n):
            self.population.append(Person(
                random.random()*_constants._AREA_WIDTH,
                random.random()*_constants._AREA_HEIGHT,
                (random.random()*2-1)*_constants._MAX_VELOCITY,
                (random.random()*2-1)*_constants._MAX_VELOCITY
            ))
        for person in self.population:
            person.update_point_object_id(self.tkwindow.generate_person_oval(person))
    def add_new_person(self):
        border = round(random.random())
        x = 0
        y = 0
        vel_x = (random.random()*2-1)*_constants._MAX_VELOCITY
        vel_y = (random.random()*2-1)*_constants._MAX_VELOCITY
        if(border):
            x = round(random.random())*_constants._AREA_WIDTH
            y = random.random()*_constants._AREA_HEIGHT
        else:
            x = random.random()*_constants._AREA_WIDTH
            y = round(random.random())*_constants._AREA_HEIGHT
        if(x <= 0 and vel_x < 0 or x >= _constants._AREA_WIDTH and vel_x > 0):
            vel_x = vel_x*(-1)
        if(y <= 0 and vel_y < 0 or y >= _constants._AREA_HEIGHT and vel_y > 0):
            vel_y = vel_y*(-1)
        self.population.append(Person(x,y,vel_x,vel_y))
        self.population[len(self.population)-1].update_point_object_id(self.tkwindow.generate_person_oval(self.population[len(self.population)-1]))
        
    def update(self, iterator):
        i = 0
        # updating position and removing person out of area
        while i < len(self.population):
            #print("i = ",i," len = ",len(self.population))
            self.population[i].update_position()
            self.tkwindow.update_person(self.population[i])
            person_oval_coords = self.tkwindow.get_person_oval_coords(self.population[i])
            if (self.population[i].location.getComponents()[0] < 0 or
                self.population[i].location.getComponents()[0] + (person_oval_coords[2] - person_oval_coords[0])/_constants._SCALE_FACTOR>  _constants._AREA_WIDTH or
                self.population[i].location.getComponents()[1] < 0 or
                self.population[i].location.getComponents()[1] + (person_oval_coords[3] - person_oval_coords[1])/_constants._SCALE_FACTOR > _constants._AREA_HEIGHT):
                    temp = random.random()
                    if(temp < 0.0):
                        if(self.population[i].location.getComponents()[0] < 0 or self.population[i].location.getComponents()[0] > _constants._AREA_WIDTH):
                            self.population[i].velocity.x = self.population[i].velocity.x*(-1)
                        if(self.population[i].location.getComponents()[1] < 0 or self.population[i].location.getComponents()[1] > _constants._AREA_HEIGHT):
                            self.population[i].velocity.y = self.population[i].velocity.y*(-1)
                    else:
                        self.tkwindow.remove_person_oval(self.population[i])
                        self.population.pop(i)
                        i = i-1
            if(iterator >= _constants._FRAMES_PER_SEC):
                self.population[i].new_velocity(_constants._MAX_VELOCITY)
            i = i+1
        updated_person: Person
        for updated_person in self.population:
            reset_infection = True
            checked_person: Person
            if (updated_person.is_resistant == True or updated_person.is_health == False):
                continue
            for checked_person in self.population:
                if(checked_person == updated_person or checked_person.is_health == True):
                    continue
                elif(distance_between_persons(checked_person,updated_person) <= _constants._INFECTION_RADIUS):
                    reset_infection = False
                    updated_person.update_infection_contact(0.025)  
            if(reset_infection == True):
                updated_person.infection_contact = 0
            if(updated_person.infection_contact > _constants._TIME_TO_INFECT):
                if(random.random() < 0.0):
                    updated_person.is_health = False 
            if(updated_person.infection_contact > 0):
                print(updated_person," - ",updated_person.infection_contact)              
        if(iterator >= _constants._FRAMES_PER_SEC):
            self.take_screen()
            iterator = 0
            self.simulation_time += 1
            if(len(self.population) < _constants._POPULATION_COUNT):
                for i in range(0,_constants._POPULATION_COUNT - len(self.population)):
                    if(random.random()<0.5):
                        self.add_new_person()
        self.tkwindow.root.after(int(1000/_constants._FRAMES_PER_SEC), self.update, iterator+1)
    def run(self):
        self.tkwindow.root.after(int(1000/_constants._FRAMES_PER_SEC), self.update, 0)
        self.tkwindow.run()

    def save(self):
        return Simulation_memento(self)
    
    def take_screen(self):
        cap = tkcap.CAP(self.tkwindow.root)
        cap.capture("screenshots/Screen-"+time.strftime("%H-%M-%S",time.localtime())+".png")
    
    def restore(self, memento):
        self.area_x = copy.deepcopy(memento.area_x)
        self.area_y = copy.deepcopy(memento.area_y)
        self.area_start_x = copy.deepcopy(memento.area_start_x)
        self.area_start_y = copy.deepcopy(memento.area_start_y)
        self.tkwindow.canvas.delete('all')
        self.population = copy.deepcopy(memento.population)
        person: Person
        for person in self.population:
            person.update_point_object_id(self.tkwindow.generate_person_oval(person))
        self.simulation_time = copy.deepcopy(memento.simulation_time)



#memento classes
class Simulation_memento():
    area_x: float
    area_y: float
    area_start_x: float 
    area_start_y: float
    population: list
    simulation_time: int

    def __init__(self, simulation: Simulation) -> None:
        self.area_x = copy.deepcopy(simulation.area_x)
        self.area_y = copy.deepcopy(simulation.area_y)
        self.area_start_x = copy.deepcopy(simulation.area_start_x)
        self.area_start_y = copy.deepcopy(simulation.area_start_y)
        self.population = copy.deepcopy(simulation.population)
        self.simulation_time = copy.deepcopy(simulation.simulation_time)
    
    def info(self):
        return f'# Simulation time: {self.simulation_time}, number of points: {len(self.population)}\n'
    
class CareTaker():
    initiator: Simulation
    mementos: list
    def __init__(self) -> None:
        self.initiator = Simulation(_constants._AREA_WIDTH,_constants._AREA_HEIGHT,"TO - lab3 symulacja")
        self.initiator.generate_list(_constants._START_POPULATION)
        self.initiator.tkwindow.root.bind('<Key>',self.on_key)
        self.mementos = list()
    
    def backup(self) -> str:
        memento = self.initiator.save()
        self.mementos.append(memento)
        return memento.info()
    
    def restore(self):
        if (len(self.mementos) == 0):
            return
        
        memento = self.mementos.pop()
        self.initiator.restore(memento)

    def run(self):
        self.initiator.run()

    def on_key(self,event):
        if event.char == 's':
            info_text = self.backup()
            self.initiator.tkwindow.on_key(event,info_text)
        elif event.char == 'r':
            self.restore()
            self.initiator.tkwindow.on_key(event,'')


def distance_between_persons(person1: Person,person2: Person):
    distance_x = abs(person1.location.getComponents()[0] - person2.location.getComponents()[0])
    distance_y = abs(person1.location.getComponents()[1] - person2.location.getComponents()[1])
    return (distance_x**2 + distance_y**2)**(1/2)

caretaker = CareTaker()
caretaker.run()


   