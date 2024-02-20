from Elements import Measure
from Entitie import Entitie
from ProbabilityDensityDistribution import ProbabilityDensityDistribution
from Printable import Printable
class Assiocation(Printable):
    def __init__(self, densitydistribution, entitie, measure) -> None:
        self.densitydistribution: ProbabilityDensityDistribution = densitydistribution
        self.entity: Entitie = entitie
        self.measure: Measure = measure
    
    def get_distribution(self) -> float:
        return self.densitydistribution.value
    
    def __repr__(self) -> str:
        return f"Assiocation(densityDistribution: {repr(self.densitydistribution)}, entity: {repr(self.entity)}, measure: {repr(self.measure)})"
    
    def __str__(self) -> str:
        return f"""Assciocation (  
        \t densityValue: {self.densitydistribution} 
        \t entity: {str(self.entity)} 
        \t measure: {str(self.measure)}  
        )"""

class Assiocations(Printable):
    def __init__(self, parentElement: Assiocation = None) -> None:
        self.assiocationList: list[Assiocation] = []
        self.EntitieMeasureList: list[tuple[Assiocation,int]] = []


    def sort_list(self):
        self.assiocationList.sort(key=lambda x: x.get_distribution(),reverse=True)
    
    def clear(self) -> None:
        self.assiocationList.clear()

    def __repr__(self) -> str:
        return f"Assiocations(assiocationList: list(Assiocation), EntitieMeasureList: list(tuple(Assiocation,int)), parentElement: {repr(self.parentElement)}, nextElement: {repr(self.nextElement)}"
    
    def __str__(self) -> str:
        return f"""Assiocations ( 
        \t Assiocations number: {len(self.assiocationList)} 
        \t entity: {str(self.assiocationList[0])} 
        \t entities measure list number: {len(self.EntitieMeasureList)} 
        )"""
   