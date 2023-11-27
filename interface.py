import os
import cv2
import time
import customtkinter
import tkinter
import tkinter.messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

from DOT_detect import DOTDetect
from DOT_crop import DOTCrop
from DOT_ocr import DOTOCR
import utils

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.text_dot_found = tkinter.StringVar(value="DOT XK 259 3311")
        self.video_path = ""

        # configure window
        self.title("CEVA 🤝 FEI")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3, 4, 5), weight=1)
        self.grid_rowconfigure((0, 1, 2, 4, 5), weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Figures")
        self.open_folder_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "open_folder_light.png")), size=(26, 26))
        self.play_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "play_light.png")), size=(26, 26))
        self.dot_path = os.path.join(image_path, "dot_example.jpg")

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="CEVA v1", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.open_video_button = customtkinter.CTkButton(self.sidebar_frame, command=self.open_video_event, text="Abrir Video", image=self.open_folder_image, compound="bottom")
        self.open_video_button.grid(row=2, column=0, padx=20, pady=20)
        self.play_video_button = customtkinter.CTkButton(self.sidebar_frame, command=self.play_video_event, text="Executar", image=self.play_image, compound="bottom")
        self.play_video_button.grid(row=3, column=0, padx=20, pady=20)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create video frame
        self.video_frame = customtkinter.CTkFrame(self)
        self.video_frame.grid(row=0, column=1, rowspan=4, columnspan=5, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0,weight=1)
        self.canvas = customtkinter.CTkCanvas(self.video_frame, bg="#dbdbdb", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # create crop frame
        self.crop_frame = customtkinter.CTkFrame(self)
        self.crop_frame.grid(row=0, column=6, rowspan=1, columnspan=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.label_zoom = customtkinter.CTkLabel(master=self.crop_frame, text="RECORTE", font=('Arial', 20))
        self.label_zoom.grid(row=0, column=0, pady=(20, 20))
        self.canvas_crop_width, self.canvas_crop_height = 200, 150
        self.canvas_crop = customtkinter.CTkCanvas(self.crop_frame, height=self.canvas_crop_height, width=self.canvas_crop_width, bg="#dbdbdb", highlightthickness=0)
        self.canvas_crop.grid(row=1, column=0, sticky="nsew")

        # create dot frame
        self.dot_frame = customtkinter.CTkFrame(self)
        self.dot_frame.grid(row=4, column=1, columnspan=6, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.dot_frame.grid_columnconfigure(0, weight=1)
        self.dot_frame.grid_rowconfigure(0, weight=1)
        self.label_dot_result = customtkinter.CTkLabel(master=self.dot_frame, textvariable=self.text_dot_found, font=('Arial', 40))
        self.label_dot_result.grid(row=0, column=0, padx=10, pady=10)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
    
    def play_video_event(self):

        DD = DOTDetect(self.resized_video_width, self.resized_video_height)
        DC = DOTCrop()
        # Calculate the delay between each frame
        delay = 1/self.video_fps

        while True:
            # Record the start time
            start_time = time.time()

            # Read the video frame
            ret, frame = self.current_video.read()

            image, all_bboxes, original_frame = DD.show_dot(ret, frame)
            if image:
                #
                # CHAMEM A FUNÇÂO DE VCS AQUI
                # EX: DOTcrop.reorient_dot()
                #
                if len(all_bboxes) > 0:
                    rotated_dot = DC.cropDot(original_frame, all_bboxes)
                    width, height = rotated_dot.size
                    custom_width, custom_height = utils.custom_resize(width, height, self.canvas_crop_width, self.canvas_crop_height)
                    resized_image = rotated_dot.resize((custom_width, custom_height))
                    img_crop = ImageTk.PhotoImage(resized_image)

                    self.crop_frame.image = img_crop
                    self.canvas_crop.create_image(0, 0, anchor='nw', image=img_crop)
                    self.crop_frame.update()

                
                #img_crop = Image.open(self.dot_path)
                #width, height = img_crop.size
                #custom_width, custom_height = utils.custom_resize(width, height, self.canvas_crop_width, self.canvas_crop_height)
                #resized_image = img_crop.resize((custom_width, custom_height))
                #img_crop = ImageTk.PhotoImage(resized_image)
                
                #self.crop_frame.image = img_crop
                #self.canvas_crop.create_image(0, 0, anchor='nw', image=img_crop)
                #self.crop_frame.update()

                # Update frame
                self.video_frame.image = image
                self.canvas.create_image(0, 0, anchor='nw', image=image)
                self.video_frame.update()
            else:
                break
            
            # Calculate the time taken to process the frame
            time_taken = time.time() - start_time
            # If the time taken is less than the delay, wait for the remaining time
            if time_taken < delay:
                time.sleep(delay - time_taken)
    

    def show_frame(self, ret, frame):
        if ret:
            frame = cv2.resize(frame, (self.resized_video_width, self.resized_video_height))
            # Convert the image from OpenCV BGR format to PIL RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the image to PIL format
            image = Image.fromarray(frame)
            # Convert the image to ImageTk format
            image = ImageTk.PhotoImage(image)
            
            # Update the image display
            self.video_frame.image = image
            self.canvas.create_image(0, 0, anchor='nw', image=image)
            self.video_frame.update()
            return True
        return False

    def open_video_event(self):
        filename = filedialog.askopenfilename(initialdir=os.path.join(os.path.dirname(os.path.realpath(__file__)), "Samples"))
        print(filename)
        self.video_path = filename
        
        cap = cv2.VideoCapture(filename)
        # Check if video opened successfully
        if not cap.isOpened(): 
            print("Error opening video file")
            return

        self.current_video = cap

        # Get the frame rate of the video
        self.video_fps = cap.get(cv2.CAP_PROP_FPS)

        # Get the resolution of the video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        aspect_ratio = width / height
        self.video_frame.update()
        self.video_frame_width = self.video_frame.winfo_width()
        self.video_frame_height = self.video_frame.winfo_height()

        # Calculate the new size of the image
        if aspect_ratio > 1:
            # If the image is wider than it is tall
            new_width = self.video_frame_width
            new_height = round(self.video_frame_width / aspect_ratio)
        else:
            # If the image is taller than it is wide
            new_height = self.video_frame_height
            new_width = round(self.video_frame_height * aspect_ratio)

        self.resized_video_width = new_width
        self.resized_video_height = new_height

        # Read the first frame
        ret, frame = cap.read()

        self.show_frame(ret, frame)