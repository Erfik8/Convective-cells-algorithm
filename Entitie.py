from Copyable import Copyable
from Measure import Measure
import copy
from operator import sub
from Printable import Printable

class EntitiesStoreMemento:
    pass

class Entitie(Copyable,Printable):
    def __init__(self) -> None:
        self.measuretuple = []
        self.motion_vector = (0,0)
        self.last_position = (0,0)
        self.last_position_error = (0,0)
    def add_pair(self,measure: Measure, timestamp: int):
        self.measuretuple.append((measure,timestamp))
        self.update_last_position()
    def is_empty(self):
        if not self.measuretuple:
            return True
        return False
    def update_last_position(self):
        if not self.measuretuple:
            return 
        last_measure: Measure
        last_measure = self.measuretuple[-1][0]
        if(self.last_position[0] != last_measure.average_x or self.last_position[1] != last_measure.average_y):
            self.last_position = (last_measure.average_x,last_measure.average_y)
            self.last_position_error = (last_measure.absoluteErr_x,last_measure.absoluteErr_y)
            if(len(self.measuretuple) == 1):
                return 
            new_motion_vector = tuple(map(sub, zip(self.measuretuple[-1],self.measuretuple[-2])))
            self.motion_vector = ((self.motion_vector[0] + new_motion_vector[0])/2,(self.motion_vector[1] + new_motion_vector[1])/2)

    def predicted_position(self):
        predicted_position = tuple(map(sum, zip(self.last_position, self.motion_vector)))
        return (predicted_position[0],predicted_position[1],self.last_position_error[0],self.last_position_error[1])
    def __copy__(self):
        return self
    def __deepcopy__(self,memo):
        new_entitie = Entitie()
        new_entitie.measuretuple = copy.deepcopy(self.measuretuple)
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
        self.entitieList = []
        self.actual_timestamp = 0
    def updateEntitie(self, entitie: Entitie, new_measure: Measure, timestamp: int):
        if entitie.is_empty() or self.entitieList.index(entitie) == ValueError:
            entitie.add_pair(new_measure,timestamp)
            self.entitieList.append(entitie)
        else:
            index_of_entity = self.entitieList.index(entitie)
            self.entitieList[index_of_entity].measuretuple.add_pair(new_measure,timestamp)
    def addEntitie(self, new_entitie: Entitie):
        self.entitieList.append(new_entitie)
    def createMemento(self):
        return EntitiesStoreMemento(self,self.entitieList,self.actual_timestamp)

    def clear(self):
        self.entitieList = []
    
    def __copy__(self):
        return self
    def __deepcopy__(self, memo):
        new_entitieStore = EntitiesStore()
        new_entitieStore.entitieList = copy.deepcopy(self.entitieList)
        new_entitieStore.actual_timestamp = self.actual_timestamp
        return new_entitieStore

class EntitiesStoreMemento:
    entitiesStoreRef: EntitiesStore
    def __init__(self, entitieStoreRef, entitieList, timestamp) -> None:
        self.entitiesStoreRef = entitieStoreRef
        self.entitieList = copy.deepcopy(entitieList)
        self.actual_timestamp = timestamp
    def restore(self):
        self.entitiesStoreRef.entitieList = copy.deepcopy(self.entitieList)
        self.entitiesStoreRef.actual_timestamp = copy.deepcopy(self.actual_timestamp)