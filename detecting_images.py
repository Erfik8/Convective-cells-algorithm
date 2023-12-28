from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog
import copy
from time import sleep
from operator import sub
import math
from Copyable import Copyable
from Oval import Oval
from Measure import Measure
from Entitie import *
from Screen import Screen
from State import StateCollection  
from ProbabilityDensityDistribution import ProbabilityDensityDistribution
from Printable import Printable
import time


class Assiocation(Printable):
    densitydistribution: ProbabilityDensityDistribution
    entity: Entitie
    measure: Measure
    def __init__(self, densitydistribution, entitie, measure) -> None:
        self.densitydistribution = densitydistribution
        self.entity = entitie
        self.measure = measure
    
    def get_distribution(self):
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
    pass
class Assiocations(Printable):
    def __init__(self, parentElement: Assiocation = None) -> None:
        self.assiocationList = []
        self.EntitieMeasureList = []
        self.parentElement = parentElement
        self.nextElement = None
    
    def create_list(self):
        rootAssiocationsList = self
        previousAssiocations = []
        while rootAssiocationsList.parentElement:
            rootAssiocationsList = rootAssiocationsList.parentElement
            previousAssiocations.append(rootAssiocationsList.assiocationList[0])
        if(rootAssiocationsList == self and not previousAssiocations):
            # this element is root - do nothing
            return
        else:
            self.assiocationList = list(filter(lambda x: x.entity not in [y.entity for y in previousAssiocations], rootAssiocationsList.assiocationList))
            self.assiocationList = list(filter(lambda x: x.measure not in [y.measure for y in previousAssiocations], self.assiocationList))
            self.assiocationList = list(filter(lambda x: x.densitydistribution.value > 0.05, self.assiocationList))
        self.sort_list()

    def create_entitie_measure_list(self):
        if not self.assiocationList:
            pass
        else:
            self.EntitieMeasureList = list(filter(lambda x: x.entity == self.assiocationList[0].entity,self.assiocationList))
            self.EntitieMeasureList = [[x,0] for x in self.EntitieMeasureList]

    def sort_list(self):
        self.assiocationList.sort(key=lambda x: x.get_distribution(),reverse=True)

    def __repr__(self) -> str:
        return f"Assiocations(assiocationList: list(Assiocation), EntitieMeasureList: list(tuple(Assiocation,int)), parentElement: {repr(self.parentElement)}, nextElement: {repr(self.nextElement)}"
    
    def __str__(self) -> str:
        return f"""Assiocations ( 
        \t parent: {'Assiocations' if self.parentElement else 'None'} 
        \t next: {'Assiocations' if self.nextElement else 'None'} 
        \t Assiocations number: {len(self.assiocationList)} 
        \t entity: {str(self.assiocationList[0])} 
        \t entities measure list number: {len(self.EntitieMeasureList)} 
        )"""
    

class GlobalAssiocation:
    def __init__(self, assiocations: Assiocations) -> None:
        self.assiocations = assiocations
    
    def calc_global_probability(self):
        best_assiocation = None
        best_probability = -1
        new_assiocation = None
        #print("entitie table size: ",len(self.assiocations.EntitieMeasureList))
        for assiocation in self.assiocations.EntitieMeasureList:
            new_assiocation = Assiocations(self.assiocations)
            # print("create assiocations list")
            new_assiocation.create_list()
            new_assiocation.assiocationList = list(filter(lambda x: x.measure != assiocation[0].measure, new_assiocation.assiocationList))
            # print("create entities list")
            new_assiocation.create_entitie_measure_list()
            new_global_assiocation = GlobalAssiocation(new_assiocation)
            probability = new_global_assiocation.calc_global_probability()
            if(probability > best_probability):
                best_probability = probability
                best_assiocation = new_assiocation
            assiocation[1] = probability
            if(self.assiocations.parentElement == None):
                log_file.write("global probability for assciocation: "+str(assiocation))
                log_file.write("blobal probability: "+str(assiocation[1]))
        if(best_probability < 0):
            return 1
        self.assiocations.nextElement = best_assiocation
        return self.assiocations.assiocationList[0].densitydistribution.value*best_probability

    
stateCollection = StateCollection()
entitiesStore = EntitiesStore()
assiocations = Assiocations()
log_file = open("log-"+time.strftime("%H-%M-%S",time.localtime())+".txt","w")


def get_pixels_in_oval(img_ref:Image, oval_pixel_list: list, x_center: int, y_center:int ):
    if(img_ref.getpixel((x_center,y_center)) == (255,255,255,255)):
        return
    oval_pixel_list.append((x_center,y_center))
    #print(oval_pixel_list)
    for x in [x_center-1,x_center,x_center+1]:
        if(x < 0 or x >= img_ref.size[0]):
            continue
        for y in [y_center-1,y_center,y_center+1]:
            if(x < x_center and y < y_center or
               x < x_center and y > y_center or 
               x > x_center and y < y_center or 
               x > x_center and y > y_center):
                continue
            if(y < 0 or y >= img_ref.size[1]):
                continue
            #if(img_ref.getpixel((x,y)) == img_ref.getpixel((x_center,y_center)) and (x,y) not in oval_pixel_list):
            if((x,y) not in oval_pixel_list):
                get_pixels_in_oval(img_ref,oval_pixel_list,x,y)


def is_in_any_oval(pixel_coords, ovals):
    oval: Oval
    for oval in ovals:
        if pixel_coords in oval.pixels:
            return True
    return False


def detect_ovals(img, screen: Screen):
    width, height = img.size
    ovals = []
    oval_iterator = 1

    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            if pixel != (255,255,255,255):  # Check if the pixel is not fully transparent
                if (is_in_any_oval((x,y),ovals) == False):
                    oval_object = Oval(str(oval_iterator))
                    oval_pixel_list = []
                    get_pixels_in_oval(img,oval_pixel_list,x,y)
                    oval_object.set_pixels_collection(oval_pixel_list)
                    oval_object.calculate_oval_bounding_box()
                    ovals.append(oval_object)
                    oval_iterator = oval_iterator+1
    screen.set_Oval_list(ovals)                 
    #print(len(ovals))

def detect_objects(screen: Screen, timestamp: int):
    measure_list = []
    oval: Oval
    for oval in screen.oval_list:
        measure = Measure(oval)
        oval.measureRef = measure
        measure_list.append(measure)
        #creating entities
        #creating predicted positions
        #assiocations
    if(timestamp == 0):
        stateCollection.clear()
        entitiesStore.clear()
    if(stateCollection.is_empty()):
        measure: Measure
        for measure in measure_list:
            new_entitie = Entitie()
            new_entitie.add_pair(measure,timestamp)
            entitiesStore.addEntitie(new_entitie)
        #print("new entities")
        #for entitie in entitiesStore.entitieList:
            #print(entitie)
    else:
        measure: Measure
        entitie: Entitie
        log_file.write("measures for timestamp: "+str(timestamp)+"\n")
        for measure in measure_list:
            log_file.write("measure "+str(measure.ovalRef.id)+" : ("+str(measure.average_x)+","+str(measure.average_y)+")\n")
        log_file.write("entities from timestamp: "+str(timestamp-1)+"\n")
        for entitie in entitiesStore.entitieList:
            log_file.write("entitie "+str(entitie.measuretuple[0][0].ovalRef.id)+" : ("+str(entitie.last_position)+") \n")
        for measure in measure_list:
            for entitie in entitiesStore.entitieList:
                #print("adding assiocation")
                #print(entitie)
                probability = ProbabilityDensityDistribution(entitie,measure.average_x,measure.average_y)
                if(probability.value >= 0.05):
                    assiocations.assiocationList.append(Assiocation(probability,entitie,measure))
        assiocation: Assiocation
        #assiocation: Assiocation
        #for assiocation in assiocations.assiocationList:
            #print(assiocation)
            #print("entitie measure: ",assiocation.entity.measuretuple[0])
        assiocations.sort_list()
        assiocations.create_entitie_measure_list()
        log_file.write("assiocations (entitie.id, measure.id, probability)\n")
        for assiocation in assiocations.assiocationList:
            log_file.write("Assiocation ("+str(assiocation.entity.measuretuple[0][0].ovalRef.id)+" , "+str(assiocation.measure.ovalRef.id)+" , "+str(assiocation.densitydistribution.value)+")\n")
        log_file.write("assiocations entitie measure list\n")
        for assiocation in [x[0] for x in assiocations.EntitieMeasureList]:
            log_file.write("Assiocation ("+str(assiocation.entity.measuretuple[0][0].ovalRef.id)+" , "+str(assiocation.measure.ovalRef.id)+" , "+str(assiocation.densitydistribution.value)+")\n")
        input("pause")
        global_probability = GlobalAssiocation(assiocations).calc_global_probability()

        #select all measurements that are not in global chain - it will be new entities
        global_chain_measurements = []

        assiocations_iterator = assiocations
        while assiocations_iterator.nextElement:
            global_chain_measurements.append(assiocations_iterator.assiocationList[0].measure)
            assiocations_iterator.assiocationList[0].entitie.add_pair(assiocations_iterator.assiocationList[0].measure,timestamp)
            log_file.write(str(assiocations_iterator))
            assiocations_iterator = assiocations_iterator.nextElement
        
        measure: Measure
        for measure in measure_list:
            if measure not in global_chain_measurements:
                # create new entitie
                new_entitie = Entitie()
                new_entitie.add_pair(measure,timestamp)
                entitiesStore.addEntitie(new_entitie)



def draw_rectangles(draw,screen: Screen):
    rect: Oval
    for rect in screen.oval_list:
        #print(rect.get_rectangle_bounding_box())
        draw.rectangle(rect.get_rectangle_bounding_box(), outline="red", width=1)

def process_images(image_paths):
    iterator = 0
    image_path: str
    for image_path in image_paths:
        new_screen = Screen(image_path, iterator)
        img = Image.open(new_screen.path)
        detect_ovals(img,new_screen)
        detect_objects(new_screen,iterator)
        stateCollection.add_state(new_screen,entitiesStore.createMemento())
        iterator += 1


def browse_image():
    file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
    if file_paths:
        process_images(file_paths)

        while True:  # Loop through screens indefinitely
            current_screen = stateCollection.get_current_screen()
            result_image = Image.open(current_screen.path)
            draw = ImageDraw.Draw(result_image)

            draw_rectangles(draw, current_screen)

            tk_img = ImageTk.PhotoImage(result_image)
            canvas.config(width=result_image.width, height=result_image.height)
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img

            root.update()
            input("wpisz cokolwiek, by kontynuowac")

            stateCollection.switch_to_next_screen()  # Switch to the next screen

# GUI setup
root = tk.Tk()
root.title("Oval Detector")

canvas = tk.Canvas(root)
canvas.pack(expand=tk.YES, fill=tk.BOTH)

browse_button = tk.Button(root, text="Browse Images", command=browse_image)
browse_button.pack()

root.mainloop()
