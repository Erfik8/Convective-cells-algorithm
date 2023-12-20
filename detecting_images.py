from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

ovals = []
oval_rectangles = []

def get_pixels_in_oval(img_ref:Image, oval_pixel_list: list, x_center: int, y_center:int ):
    if(img_ref.getpixel((x_center,y_center)) == (255,255,255,255)):
        return
    oval_pixel_list.append((x_center,y_center))
    #print(oval_pixel_list)
    for x in [x_center-1,x_center,x_center+1]:
        if(x < 0 or x >= img_ref.size[0]):
            continue
        for y in [y_center-1,y_center,y_center+1]:
            if(y < 0 or y >= img_ref.size[1]):
                continue
            #if(img_ref.getpixel((x,y)) == img_ref.getpixel((x_center,y_center)) and (x,y) not in oval_pixel_list):
            if((x,y) not in oval_pixel_list):
                get_pixels_in_oval(img_ref,oval_pixel_list,x,y)


def is_in_any_oval(pixel_coords):
    for oval in ovals:
        if pixel_coords in oval:
            return True
    return False


def detect_ovals(image_path):
    img = Image.open(image_path)
    width, height = img.size


    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            if pixel != (255,255,255,255):  # Check if the pixel is not fully transparent
                if (is_in_any_oval((x,y)) == False):
                    oval_pixel_list = []
                    get_pixels_in_oval(img,oval_pixel_list,x,y)
                    ovals.append(oval_pixel_list)
                    # Determine the bounding box for the oval
                    left, top, right, bottom = find_oval_bounding_box(img, oval_pixel_list)
                    oval_rectangles.append((left, top, right, bottom))
    print(len(ovals))


def find_oval_bounding_box(img, oval_pixel_list):
    
    x_min = -1
    x_max = -1
    y_min = -1
    y_max = -1
    for coords in oval_pixel_list:
        if (x_min < 0 or coords[0] < x_min):
            x_min = coords[0]
        if (x_max < 0 or coords[0] > x_max):
            x_max = coords[0]
        if (y_min < 0 or coords[1] < y_min):
            y_min = coords[1]
        if (y_max < 0 or coords[1] > y_max):
            y_max = coords[1]
    return x_min,y_min,x_max,y_max


def draw_rectangles(canvas, rectangles):
    for rect in rectangles:
        print(rect)
        canvas.create_rectangle(rect, outline="red", width=1)

def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        detect_ovals(file_path)
        img = Image.open(file_path)
        tk_img = ImageTk.PhotoImage(img)
        canvas.config(width=img.width, height=img.height)
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        draw_rectangles(canvas, oval_rectangles)
        canvas.image = tk_img

# GUI setup
root = tk.Tk()
root.title("Oval Detector")

canvas = tk.Canvas(root)
canvas.pack(expand=tk.YES, fill=tk.BOTH)

browse_button = tk.Button(root, text="Browse Image", command=browse_image)
browse_button.pack()

root.mainloop()
