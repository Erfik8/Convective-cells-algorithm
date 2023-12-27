from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog
import copy
from abc import ABC, abstractclassmethod
from time import sleep
from operator import sub
import math

class Copyable(ABC):
    @abstractclassmethod
    def __copy__(self):
        pass

    @abstractclassmethod
    def __deepcopy__(self, memo):
        pass
class Oval(Copyable):
    pass

class Oval(Copyable):
    pixels: list
    def __init__(self) -> None:
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
        new_oval = Oval()
        new_oval.set_pixels_collection(self.pixels)
        new_oval.calculate_oval_bounding_box()
        new_oval.measureRef = self.measureRef
        return new_oval

    def __eq__(self, value: Oval) -> bool:
        temp_list_is_equals = set(self.pixels) == set(value.pixels)
        return self.measureRef == value.measureRef and self.x_max == value.x_max and self.x_min == value.x_min and self.y_min == value.y_min and self.y_max == value.y_max and temp_list_is_equals
    
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
        self.average_x /= count
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
        

class Entitie(Copyable):
    def __init__(self) -> None:
        self.measuretuple = []
        self.motion_vector = (0,0)
        self.last_position = (0,0)
        self.last_position_error = (0,0)
    def add_pair(self,measure: Measure, timestamp: int):
        self.measuretuple.append((measure,timestamp))
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
    
class EntitiesStoreMemento:
    pass

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
    
class Screen:
    def __init__(self, path, timestamp) -> None:
        self.path = path
        self.oval_list = []
        self.measures = []
        self.timestamp = timestamp

    def set_Oval_list(self, oval_list: list):
        self.oval_list = copy.deepcopy(oval_list)

class StateCollection:
    def __init__(self) -> None:
        self.states = []
        self.screen_width = 0
        self.screen_height = 0
        self.current_screen_index = 0  # Added to keep track of the current screen index

    def add_state(self,screen: Screen,entities: EntitiesStoreMemento):
        if(self.screen_height != 0 or self.screen_width != 0):
            img = Image.open(screen.path)
            if(img.width != self.screen_width or img.height != self.screen_height):
                print("Images have different dimensions")
                exit(1)
            else:
                self.states.append((screen,entities))
        else:
            self.states.append((screen,entities))
            img = Image.open(screen.path)
            self.screen_height = img.height
            self.screen_width = img.width

    def get_current_screen(self):
        return self.states[self.current_screen_index][0]

    def switch_to_next_screen(self):
        self.current_screen_index = (self.current_screen_index + 1) % len(self.states)

    
stateCollection = StateCollection()
entitiesStore = EntitiesStore()


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

    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            if pixel != (255,255,255,255):  # Check if the pixel is not fully transparent
                if (is_in_any_oval((x,y),ovals) == False):
                    oval_object = Oval()
                    oval_pixel_list = []
                    get_pixels_in_oval(img,oval_pixel_list,x,y)
                    oval_object.set_pixels_collection(oval_pixel_list)
                    oval_object.calculate_oval_bounding_box()
                    ovals.append(oval_object)
    screen.set_Oval_list(ovals)                 
    print(len(ovals))

def detect_objects(screen: Screen):
    oval: Oval
    for oval in screen.oval_list:
        measure = Measure(oval)
        oval.measureRef = measure



def draw_rectangles(draw,screen: Screen):
    rect: Oval
    for rect in screen.oval_list:
        print(rect.get_rectangle_bounding_box())
        draw.rectangle(rect.get_rectangle_bounding_box(), outline="red", width=1)

def process_images(image_paths):
    iterator = 0
    for image_path in image_paths:
        new_screen = Screen(image_path, iterator)
        img = Image.open(new_screen.path)
        detect_ovals(img,new_screen)
        new_entetie = Entitie()
        entitiesStore.addEntitie(new_entetie)
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
            sleep(0.5)

            stateCollection.switch_to_next_screen()  # Switch to the next screen

# GUI setup
root = tk.Tk()
root.title("Oval Detector")

canvas = tk.Canvas(root)
canvas.pack(expand=tk.YES, fill=tk.BOTH)

browse_button = tk.Button(root, text="Browse Images", command=browse_image)
browse_button.pack()

root.mainloop()
