from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog
import copy
from abc import ABC, abstractclassmethod
from time import sleep

class Copyable(ABC):
    @abstractclassmethod
    def __copy__(self):
        pass

    @abstractclassmethod
    def __deepcopy__(self, memo):
        pass


class Oval(Copyable):
    pixels: list
    def __init__(self) -> None:
        self.pixels = []
        self.x_min = -1
        self.x_max = -1
        self.y_min = -1
        self.y_max = -1
    
    def set_pixels_collection(self,pixels_collection:list):
        self.pixels = copy.deepcopy(pixels_collection)

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
        return new_oval
    
class Screen:
    def __init__(self, path) -> None:
        self.path = path
        self.oval_list = []
        self.measures = []

    def set_Oval_list(self, oval_list: list):
        self.oval_list = copy.deepcopy(oval_list)

class ScreenCollection:
    def __init__(self) -> None:
        self.screens = []
        self.screen_width = 0
        self.screen_height = 0
        self.current_screen_index = 0  # Added to keep track of the current screen index

    def add_screen(self,screen: Screen):
        if(self.screen_height != 0 or self.screen_width != 0):
            img = Image.open(screen.path)
            if(img.width != self.screen_width or img.height != self.screen_height):
                print("Images have different dimensions")
                exit(1)
            else:
                self.screens.append(screen)
        else:
            self.screens.append(screen)
            img = Image.open(screen.path)
            self.screen_height = img.height
            self.screen_width = img.width

    def get_current_screen(self):
        return self.screens[self.current_screen_index]

    def switch_to_next_screen(self):
        self.current_screen_index = (self.current_screen_index + 1) % len(self.screens)

    
screenCollection = ScreenCollection()


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


def draw_rectangles(draw,screen: Screen):
    rect: Oval
    for rect in screen.oval_list:
        print(rect.get_rectangle_bounding_box())
        draw.rectangle(rect.get_rectangle_bounding_box(), outline="red", width=1)

def process_images(image_paths):
    for image_path in image_paths:
        new_screen = Screen(image_path)
        img = Image.open(new_screen.path)
        detect_ovals(img,new_screen)
        screenCollection.add_screen(new_screen)


def browse_image():
    file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
    if file_paths:
        process_images(file_paths)

        while True:  # Loop through screens indefinitely
            current_screen = screenCollection.get_current_screen()
            result_image = Image.open(current_screen.path)
            draw = ImageDraw.Draw(result_image)

            draw_rectangles(draw, current_screen)

            tk_img = ImageTk.PhotoImage(result_image)
            canvas.config(width=result_image.width, height=result_image.height)
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img

            root.update()
            sleep(0.5)

            screenCollection.switch_to_next_screen()  # Switch to the next screen

# GUI setup
root = tk.Tk()
root.title("Oval Detector")

canvas = tk.Canvas(root)
canvas.pack(expand=tk.YES, fill=tk.BOTH)

browse_button = tk.Button(root, text="Browse Images", command=browse_image)
browse_button.pack()

root.mainloop()
