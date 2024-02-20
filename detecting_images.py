from __future__ import annotations
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog
import copy
from time import sleep
from operator import sub
import math
from Copyable import Copyable
from Elements import Oval, Measure
from Entitie import *
from Screen import Screen
from State import StateCollection  
from ProbabilityDensityDistribution import ProbabilityDensityDistribution
from Printable import Printable
from Assiocations import Assiocation, Assiocations
import time

#słownik
# class Oval - przechowuje pojedyńczy 'Blob' z bitmapy w postaci listy pixeli. Do celów dalszych obliczeń ma informacje o granicznych pixelach (góra-dół, lewo-prawo)
# class Measure - przechowuje informacje na temat środka 'Bloba' (obliczony zgodnie ze wzorem z pliku) oraz o błędzie pomiaru (również wzór z pliku)
#   klasy Measure i Oval są powiązane ze sobą agregacją całkowitą
# class Screen - przechowuje informacje o konkretnej bitmapie w danej jednostce czasu. Zawiera wszystkie klasy Oval oraz Measure dla danego momentu czasu
# class Entitie - Zawiera informacje o jednym obiekcie z całej symulacji. Obiekt to jest seria 'Blobów' oraz ich odcinków czasowych. 
#   klasa ma listę dwójek (Measure,int). W zależności jak długo obiekt znajdował się w symulacji, tyle będzie dwójek w liście
#   Oprócz tego Entitie pozwala obliczyć przewidywane położenie oraz ma informacje o wektorze prędkości
# class StateCollection - Zawiera kolecję wszystkich scen oraz stanie oiektów dla danej sceny
#   klasa ma listę dwójek (Screen,EntityMemento). Dla danego odcinka czasu zapisana jest scena, ze wszystkimi 'Blobami', oraz stan obiektów 
# class ProbabilityDensityDistribution - zawierą wynik prawdopodobieństwa przypisania pomiaru z czasu T dla Entity z czasu T-1
# class Asiocation - Zawiera trójkę klas ProbabilityDensityDistribution, Entity i Measure
#   każdy obiekt Assiocation jest tworzony w wyniku łączenia każdego Entity z poprzedniego pomiaru z każdym pomiarem Measure
#   z nowego pomiaru. Następnie dla każdej takiej dwójki jest tworzony obiekt z prawdopodobieństwem i obliczany
# class Assiocations - Zawiera listę obiektów Assiocation dla danej sceny
 

# funkcja rekurencyjna
# dict = referencja do globalnej biblioteki
# row - numer wiersza do sprawdzenia
# measure list - lista pomiarów, które zawierają już klasy Assiocations z poprzednio sprawdzonych elementów
# funkcja zwraca globalne prawdopodobieństwo oraz łancuch - listę Assiocations dla najbardziej prawdopodobnej kombinacji
def find_global_probability_in_dict(dict: list[list[int,list[Assiocation]]],row: int, measure_list: list) -> list[float,list[Assiocation]]:
    if(row >= len(dict)):
        return [1,[]]
    best_probability = -1
    bestsubchain = []
    best_assiocation = None
    for entity_assiocations in dict[row][1]:
        if(entity_assiocations.measure in measure_list):
            continue
        new_measure_list = copy.copy(measure_list)
        new_measure_list.append(entity_assiocations.measure)
        probability, subchain = find_global_probability_in_dict(dict,row+1,new_measure_list)
        if(probability > best_probability):
            best_probability = probability
            bestsubchain = subchain
            best_assiocation = entity_assiocations
    if best_probability == -1 or best_assiocation == None:
        #end of chain reached - return chain probability (chain length/dict length)
        return [(row-1)/len(dict)**2,[]]
    else:
        bestsubchain.append(best_assiocation)
        return [best_probability*best_assiocation.densitydistribution.value,bestsubchain]



    
stateCollection = StateCollection()
entitiesStore = EntitiesStore()
assiocations = Assiocations()
#log_file = open("log-"+time.strftime("%H-%M-%S",time.localtime())+".txt","w")



def get_pixels_in_oval(img_ref:Image, oval_pixel_list: list, x_center: int, y_center:int ):
    if(img_ref.getpixel((x_center,y_center)) == (0,0,0,255)):
        return
    oval_pixel_list.append((x_center,y_center))
    #print(oval_pixel_list)
    for x in [x_center-2,x_center-1,x_center,x_center+1,x_center+2]:
        if(x < 0 or x >= img_ref.size[0]):
            continue
        for y in [y_center-2,y_center-1,y_center,y_center+1,y_center+2]:
            if(y < 0 or y >= img_ref.size[1]):
                continue
            if(abs(x - x_center) + abs(y - y_center) >= 3):
                continue
            if(abs(x - x_center) == 1 or abs(y-y_center) == 1):
                if(img_ref.getpixel((x,y)) != (0,0,0,255)):
                    oval_pixel_list.append((x,y))
            if(x == (x_center - 2) and y == y_center or
               x == (x_center + 2) and y == y_center or
               x == x_center and y == (y_center - 2) or
               x == x_center and y == (y_center + 2)):
                if((x,y) not in oval_pixel_list):
                    get_pixels_in_oval(img_ref,oval_pixel_list,x,y)

# sprawdza, czy któryś ze sprawdzanych pixeli nie znajduje się w już wykrytym 'Blobie'                
def is_in_any_oval(pixel_coords, ovals):
    oval: Oval
    for oval in ovals:
        if pixel_coords in oval.pixels:
            return True
    return False

#wykrywanie Blobów z danego obrazu
def detect_ovals(img: Image, screen: Screen):
    width, height = img.size
    ovals = []
    oval_iterator = 1

    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            #print(pixel)
            if pixel != (0,0,0,255):  # Check if the pixel is not fully transparent
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
    measure_list: list[Measure] = []
    entitiesStore.current_timestamp = timestamp
    oval: Oval
    for oval in screen.oval_list:
        measure = Measure(oval)
        oval.measureRef = measure
        measure_list.append(measure)
    screen.set_Measure_list(measure_list)
    # wykrywanie obiektów dla 1 obrazu
    if(timestamp == 0):
        stateCollection.clear()
        entitiesStore.clear()
    if(stateCollection.is_empty()):
        measure: Measure
        for measure in measure_list:
            new_entitie = Entitie()
            entitiesStore.updateEntitie(new_entitie,measure,timestamp)
    # wykrywanie obiektów dla kolejnych obrazów - caly program zawiera już wczytane jakieś dane
    else:
        measure: Measure
        entitie: Entitie
        #log_file.write("measures for timestamp: "+str(timestamp)+"\n")
        #for measure in measure_list:
            #log_file.write("measure "+str(measure.ovalRef.id)+" : ("+str(measure.average_x)+","+str(measure.average_y)+")\n")
        #log_file.write("entities from timestamp: "+str(timestamp-1)+"\n")
        #for entitie in entitiesStore.get_entities_by_timestamp(timestamp-1):
            #log_file.write("entitie "+str(entitie.id)+" : ("+str(entitie.last_position)+") \n")
        #tworzenie list Assiocations
        for measure in measure_list:
            for entitie in entitiesStore.get_entities_by_timestamp(timestamp-1):
                probability = ProbabilityDensityDistribution(entitie,measure)
                if(probability.value >= 0.05):
                    assiocations.assiocationList.append(Assiocation(probability,entitie,measure))

        # specyficzna biblioteka
        # klasy Assiocation są poukładane w wiersze, dla każdego obiektu Entitie
        # Dla przykładu
        # lista pomiarów
        # M = [m1, m2, m3, m4]
        # lista obiektów
        # E = [e1, e2, e3, e4]
        # lista Assiocations
        # A = [e1m1, e1m2, e1m3, e1m4, e2m1, ...., e4m3, e4m4]
        # Biblioteka
        # dict = [
        #           [1,[e1m1, e1m2, e1m3, e1m4]],
        #           [2,[e2m1, e2m2, e2m3, e2m4]],
        #           ...
        #        ]
        assiocation_dict: list[list[int,list[Assiocation]]] = []
        for entitie in entitiesStore.get_entities_by_timestamp(timestamp-1):
            assiocation_dict.append([entitie.id,[x for x in assiocations.assiocationList if x.entity.id == entitie.id]])
            assiocation_dict[-1][1].sort(key=lambda x: x.get_distribution(),reverse=True)
            #print(f"id: {entitie.id} list size: {len(assiocation_dict[-1][1])} biggest probability: {0 if len(assiocation_dict[-1][1]) == 0 else assiocation_dict[-1][1][0].densitydistribution.value}")
        

        assiocation_dict.sort(key=lambda x: 0 if len(x[1]) == 0 else x[1][0].densitydistribution.value,reverse=True)

        probability, chain = find_global_probability_in_dict(assiocation_dict,0,[])

        for assiocation in chain:
            print(("Assiocation ("+str(assiocation.entity.id)+" , "+str(assiocation.measure.ovalRef.id)+" , "+str(assiocation.densitydistribution.value)+")\n"))

        # lista zawiera pomiary, które są przypisane do klasy Assiocations. Posłuży do sprawdzenia, czy na mapie nie ma nowych obiektów
        global_chain_measurements = []

        assiocation_iterator:Assiocation
        for assiocation_iterator in chain:
            global_chain_measurements.append(assiocation_iterator.measure)
            entitiesStore.updateEntitie(assiocation_iterator.entity,assiocation_iterator.measure,timestamp)
            #log_file.write(str(assiocation_iterator))

        measure: Measure
        for measure in measure_list:
            if measure not in global_chain_measurements:
                # create new entitie
                new_entitie = Entitie()
                entitiesStore.updateEntitie(new_entitie,measure,timestamp)

        assiocations.clear()


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

def draw_entitie_line(draw: ImageDraw, entitie: Entitie) -> None:
    measureT: tuple[Measure,int]
    previousMeasureT: tuple[Measure,int] = None
    entitie.measuretuple.sort(key=lambda x: x[1])
    for measureT in entitie.measuretuple:
        if previousMeasureT != None:
            # draw only dot
            lineStartPoint = (previousMeasureT[0].average_x,previousMeasureT[0].average_y)
            lineEndPoint = (measureT[0].average_x,measureT[0].average_y)
            draw.line((lineStartPoint[0],lineStartPoint[1],lineEndPoint[0],lineEndPoint[1]), fill='red')
        draw.ellipse((measureT[0].average_x - 1, measureT[0].average_y-1, measureT[0].average_x+1, measureT[0].average_y+1),fill='red')
        previousMeasureT = measureT

def browse_image():
    file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
    if file_paths:
        process_images(file_paths)

        while True:  # Loop through screens indefinitely
            current_screen = stateCollection.get_current_screen()
            current_entities = stateCollection.get_current_entities()
            result_image = Image.open(current_screen.path)
            draw = ImageDraw.Draw(result_image)

            for entitie in current_entities.get_entities_by_timestamp(current_entities.current_timestamp):
                draw_entitie_line(draw,entitie)

            tk_img = ImageTk.PhotoImage(result_image)
            canvas.config(width=result_image.width, height=result_image.height)
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img

            root.update()
            sleep(0.08)
            #input("wpisz cokolwiek, by kontynuowac")

            stateCollection.switch_to_next_screen()  # Switch to the next screen

# GUI setup
root = tk.Tk()
root.title("Oval Detector")

canvas = tk.Canvas(root)
canvas.pack(expand=tk.YES, fill=tk.BOTH)

browse_button = tk.Button(root, text="Browse Images", command=browse_image)
browse_button.pack()

root.mainloop()
