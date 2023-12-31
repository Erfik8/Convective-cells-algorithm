from __future__ import annotations
from Copyable import Copyable
from Elements import Measure
import copy
from operator import sub
from Printable import Printable

class Entitie(Copyable,Printable):
    count: int = 0
    
    def __init__(self) -> None:
        self.measuretuple: list[tuple[Measure,int]] = []
        self.motion_vector: tuple[float,float] = (0.0,0.0)
        self.last_position: tuple[float,float] = (0.0,0.0)
        self.last_position_error: tuple[float,float] = (0.0,0.0)
        self.id = Entitie.count
        Entitie.count += 1

    def add_pair(self,measure: Measure, timestamp: int) -> None:
        self.measuretuple.append((measure,timestamp))
        self.__update_last_position()
    def is_empty(self) -> bool:
        if not self.measuretuple:
            return True
        return False
    def __update_last_position(self) -> None:
        if not self.measuretuple:
            return 
        last_measure: Measure = self.measuretuple[-1][0]
        if(self.last_position[0] != last_measure.average_x or self.last_position[1] != last_measure.average_y):
            self.last_position = (last_measure.average_x,last_measure.average_y)
            self.last_position_error = (last_measure.absoluteErr_x,last_measure.absoluteErr_y)
            if(len(self.measuretuple) == 1):
                return 
            new_motion_vector = [0,0]
            new_motion_vector[0] = self.measuretuple[-1][0].get_average_coords()[0] - self.measuretuple[-2][0].get_average_coords()[0]
            new_motion_vector[1] = self.measuretuple[-1][0].get_average_coords()[1] - self.measuretuple[-2][0].get_average_coords()[1]
            self.motion_vector = (new_motion_vector[0],new_motion_vector[1])

    def predicted_position(self) -> tuple[float,float,float,float]:
        predicted_position = tuple(map(sum, zip(self.last_position, self.motion_vector)))
        return (predicted_position[0],predicted_position[1],self.last_position_error[0],self.last_position_error[1])
    
    def get_measure_by_timestamp(self, timestamp: int) -> Measure:
        return next(x[0] for x in self.measuretuple if x[1] == timestamp)

    def __del__(self):
        Entitie.count -= 1
        super().__del__()
    
    def __copy__(self) -> Entitie:
        return self
    def __deepcopy__(self,memo) -> Entitie:
        new_entitie = Entitie()
        new_entitie.measuretuple = copy.copy(self.measuretuple)
        new_entitie.motion_vector = copy.deepcopy(self.motion_vector)
        new_entitie.last_position_error = copy.deepcopy(self.last_position)
        new_entitie.last_position = copy.deepcopy(self.last_position)
        new_entitie.id = self.id
        return new_entitie
    def __repr__(self) -> str:
        return f"Entitie(measureTuple: Tuple(Measure, int), motionVector: Tuple(int,int), lastPosition: Tuple(int,int), lastPositionError: Tuple(int,int))"
    def __str__(self) -> str:
        return f"""Entitie (
        measurestuple: {self.measuretuple}
        motion vector: {self.motion_vector}
        lastPosition: {self.last_position}
        )
        """
    


class EntitiesStore(Copyable):
    def __init__(self) -> None:
        self.entitieList: list[Entitie] = []
        self.current_timestamp: int = 0
    def updateEntitie(self, entitie: Entitie, new_measure: Measure, timestamp: int) -> None:
        if entitie.is_empty() or self.entitieList.index(entitie) == ValueError:
            entitie.add_pair(new_measure,timestamp)
            self.entitieList.append(entitie)
        else:
            index_of_entity = self.entitieList.index(entitie)
            self.entitieList[index_of_entity].add_pair(new_measure,timestamp)
    def addEntitie(self, new_entitie: Entitie) -> None:
        self.entitieList.append(new_entitie)
    def createMemento(self) -> EntitiesStoreMemento:
        return EntitiesStoreMemento(self,self.entitieList)

    def clear(self) -> None:
        self.entitieList = []

    def get_entities_by_timestamp(self,timestamp: int) -> list[Entitie]:
        return list(filter(lambda x: timestamp in  [y[1] for y in x.measuretuple],self.entitieList))
    
    def __copy__(self) -> EntitiesStore:
        return self
    def __deepcopy__(self, memo) -> EntitiesStore:
        new_entitieStore = EntitiesStore()
        new_entitieStore.entitieList = copy.deepcopy(self.entitieList)
        new_entitieStore.current_timestamp = self.current_timestamp
        return new_entitieStore

class EntitiesStoreMemento:
    def __init__(self, entitieStoreRef: EntitiesStore, entitieList: list[Entitie]) -> None:
        self.entitiesStoreRef: EntitiesStore = entitieStoreRef
        self.entitieList: list[Entitie] = copy.deepcopy(entitieList)
        self.current_timestamp = copy.deepcopy(entitieStoreRef.current_timestamp)
    def restore(self):
        self.entitiesStoreRef.entitieList = copy.deepcopy(self.entitieList)
        self.entitiesStoreRef.current_timestamp = self.current_timestamp
    def rester_to_new(self) -> EntitiesStore:
        new_entitie = EntitiesStore()
        new_entitie.entitieList = copy.deepcopy(self.entitieList)
        new_entitie.current_timestamp = self.current_timestamp
        return new_entitie