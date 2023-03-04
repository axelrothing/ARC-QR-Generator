from tkinter import *
import pyqrcode
import png
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import threading
import webbrowser
import os
import datetime
import sqlite3

VERSION = "3.0"

conn = sqlite3.connect("qr_database.db")
cursor = conn.cursor()

size_root = Tk()

screen_width = size_root.winfo_screenwidth()
screen_height = size_root.winfo_screenheight()

size_root.destroy()

print("Screen width:", screen_width)
print("Screen height:", screen_height)

root = Tk()
root.title("ARC QR Code Generator")
root.iconbitmap("icon.ico")
root.configure(bg="#98FF98")

################################################################
#function section

def generate_wifi():
    global choice_label2, qr_entry2

    choice_label.configure(text="Wifi Name")

    choice_label2 = Label(master=input_frame, text="Wifi Password", bg=GREEN_COLOR, font=(FONT, CHOICE_FONT_SIZE))
    choice_label2.grid(row=1, column=0, padx=CHOICE_PADX, pady=CHOICE_PADY)

    qr_entry2 = ttk.Entry(master=input_frame, font=(FONT, ENTRY_FONT_SIZE), width=ENTRY_WIDTH)
    qr_entry2.grid(row=1, column=1, padx=ENTRY_PADX, pady=ENTRY_PADY)

def generate_contact():
    global choice_label_phone, choice_entry_phone
    global choice_label_email, choice_entry_email
    global choice_label_address, choice_entry_address

    choice_label.configure(text="Name")

    choice_label_phone = Label(master=input_frame, text="Phone", bg=GREEN_COLOR, font=(FONT, CHOICE_FONT_SIZE))
    choice_label_phone.grid(row=1, column=0, padx=CHOICE_PADX, pady=CHOICE_PADY)

    choice_entry_phone = ttk.Entry(master=input_frame, font=(FONT, ENTRY_FONT_SIZE), width=ENTRY_WIDTH)
    choice_entry_phone.grid(row=1, column=1, padx=ENTRY_PADX, pady=ENTRY_PADY)
    choice_entry_phone.insert(0, "+47-")

    choice_label_email = Label(master=input_frame, text="Email", bg=GREEN_COLOR, font=(FONT, CHOICE_FONT_SIZE))
    choice_label_email.grid(row=2, column=0, padx=CHOICE_PADX, pady=CHOICE_PADY)

    choice_entry_email = ttk.Entry(master=input_frame, font=(FONT, ENTRY_FONT_SIZE), width=ENTRY_WIDTH)
    choice_entry_email.grid(row=2, column=1, padx=ENTRY_PADX, pady=ENTRY_PADY)

    choice_label_address = Label(master=input_frame, text="Address", bg=GREEN_COLOR, font=(FONT, CHOICE_FONT_SIZE))
    choice_label_address.grid(row=3, column=0, padx=CHOICE_PADX, pady=CHOICE_PADY)

    choice_entry_address = ttk.Entry(master=input_frame, font=(FONT, ENTRY_FONT_SIZE), width=ENTRY_WIDTH)
    choice_entry_address.grid(row=3, column=1, padx=ENTRY_PADX, pady=ENTRY_PADY)

def update_label():
    choice = radio_var.get()

    try:
        choice_label2.destroy()
        qr_entry2.destroy()
    except:
        pass
    try:
        choice_label_phone.destroy()
        choice_entry_phone.destroy()
        choice_label_email.destroy()
        choice_entry_email.destroy()
        choice_label_address.destroy()
        choice_entry_address.destroy()
    except:
        pass

    choice_label.configure(text=choice.title())

    qr_entry.delete(0, END)

    if choice == "url":
        qr_entry.insert(0, "https://www.")
    elif choice == "phone":
        qr_entry.insert(0, "+47-")
    elif choice == "wifi":
        generate_wifi()
    elif choice == "contact":
        generate_contact()

def clear():
    update_label()
    qr_label.configure(image="")

def create():
    input_path = filedialog.asksaveasfilename(title="Save QR Image", filetypes=(("PNG File", ".png"), ("All Files", "*.*")))
    img_scale = int(scale_slider.get())

    if not input_path:
        return

    choice = radio_var.get()
    qr_input = qr_entry.get()

    if not input_path.endswith(".png"):
        input_path = f"{input_path}.png"

    if choice == "email":
        get_code = pyqrcode.create(f"mailto:{qr_input}")
    elif choice == "phone":
        get_code = pyqrcode.create(f"tel:{qr_input}")
    elif choice == "wifi":
        ssid = qr_entry.get()
        password = qr_entry2.get()
        get_code = pyqrcode.create(f"WIFI:S:{ssid};T:WPA;P:{password};")
    elif choice == "contact":
        name = qr_entry.get()
        phone = choice_entry_phone.get()
        email = choice_entry_email.get()
        address = choice_entry_address.get()

        if not name:
            messagebox.showwarning(title="Warning", message="Name field is required!")
            return

        qr_data = f"MECARD:N:{name}"
        if phone:
            qr_data += f";TEL:{phone}"
        if email:
            qr_data += f";EMAIL:{email}"
        if address:
            qr_data += f";ADR:{address}"
        qr_data += ";;"

        get_code = pyqrcode.create(qr_data)

    else:
        get_code = pyqrcode.create(qr_input)

    #get_code.png(input_path, scale=5)
    get_code.png(input_path, scale=img_scale)

    global get_image
    get_image = ImageTk.PhotoImage(Image.open(input_path))
    qr_label.configure(image=get_image)

    print("generated qr_code!")

    now = datetime.datetime.now()
    date = now.strftime("%d-%m-%Y")
    qr_type = choice.title()

    cursor.execute("INSERT INTO qr_table VALUES (?, ?, ?)", (qr_type, date, input_path))
    conn.commit()

    image = Image.open(input_path)
    width, height = image.size
    print("Image size:", width, "x", height)

    img_root = Toplevel(bg=PINK_COLOR, master=root)
    img_root.title("QR")
    img_root.iconbitmap("icon.ico")

    def exit_window():
        img_root.destroy()

    qr_toplevel_label = Label(master=img_root, text="", image=get_image)
    qr_toplevel_label.pack(padx=TITLE_PADX, pady=TITLE_PADY)

    exit_btn = Button(master=img_root, text="X", font=(FONT, BUTTON_FONT_SIZE), command=exit_window, bg="#e5383b")
    exit_btn.pack(padx=BUTTON_PADX, pady=BUTTON_PADY)

    img_root.mainloop()



def check_for_update():
    response = requests.get("https://axeldronephoto.wixsite.com/arc-qr-generator")

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, "html.parser")

        span = soup.find("span", style="font-family:proxima-n-w01-reg,proxima-n-w05-reg,sans-serif;")

        text = span.text

        print(text)

        if text != VERSION:
            print("Warning: new version available")
            choice = messagebox.askyesno(title="Update Available!", message="New version available, do you want to update?")
            if not choice:
                return
            messagebox.showwarning(title="Warning", message="Remember to uninstall the app first, search up remove programs in the windows search bar, then search up arc qr generator, when you have found it, click on the 3 dots and click uninstall, when you are finished, come back and click ok.")
            print("Opening link!")
            webbrowser.open("https://bit.ly/arc-qr-generator")

    else:
        print("Request failed with status code", response.status_code)

def set_slider_label(event):
    try:
        slider_label.configure(text=int(scale_slider.get()))
    except:
        pass

#######################################
# 3.5

# GREEN_COLOR = "#98FF98"
# BLUE_COLOR = "#00FFFF"
# PINK_COLOR = "#fcc6d4"

def show_all():
    created_root = Toplevel(master=root)

    created_root.title("ARC QR Code Generator")
    created_root.iconbitmap("icon.ico")
    created_root.configure(bg="#98FF98")

    #functions

    def update_listbox():
        pass

    def select():
        pass

    def delete():
        pass

    def open_folder():
        pass

    #gui

    created_title = Label(master=created_root, text="Created QR Codes", font=(FONT, TITLE_FONT_SIZE), bg=GREEN_COLOR)
    created_title.grid(row=0, column=0, padx=TITLE_PADX, pady=TITLE_PADY)

    controls_title = Label(master=created_root, text="Controls", font=(FONT, TITLE_FONT_SIZE), bg=GREEN_COLOR)
    controls_title.grid(row=0, column=1, padx=TITLE_PADX, pady=TITLE_PADY)

    listbox_frame = Frame(master=created_root, bg=GREEN_COLOR)
    listbox_frame.grid(row=1, column=0, padx=OTHER_PADX, pady=OTHER_PADY)

    created_listbox = Listbox(master=listbox_frame, width=LISTBOX_WIDTH, font=(FONT, LISTBOX_FONT_SIZE), height=LISTBOX_HEIGHT, bg=PINK_COLOR, selectbackground=BLUE_COLOR, selectforeground="white")
    created_listbox.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    controls_frame = Frame(master=created_root, bg=GREEN_COLOR)
    controls_frame.grid(row=1, column=1, padx=OTHER_PADX, pady=OTHER_PADY)

    select_btn = Button(master=controls_frame, text="Select", bg=BLUE_COLOR, width=CREATED_BUTTON_WIDTH, font=(FONT, CREATED_BUTTON_FONT_SIZE), command=select)
    select_btn.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    delete_btn = Button(master=controls_frame, text="Delete", bg=BLUE_COLOR, width=CREATED_BUTTON_WIDTH, font=(FONT, CREATED_BUTTON_FONT_SIZE), command=delete)
    delete_btn.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    open_btn = Button(master=controls_frame, text="Show In Folder", bg=BLUE_COLOR, width=CREATED_BUTTON_WIDTH, font=(FONT, CREATED_BUTTON_FONT_SIZE), command=open_folder)
    open_btn.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    created_qr_frame = LabelFrame(master=controls_frame, text="QR Code", font=(FONT, CREATED_FRAME_FONT_SIZE), bg=GREEN_COLOR)
    created_qr_frame.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    created_qr_label = Label(master=created_qr_frame, text="", bg=GREEN_COLOR)
    created_qr_label.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    file_label = Label(master=created_qr_frame, text="", bg=GREEN_COLOR, font=(FONT, CREATED_PATH_FONT_SIZE))
    file_label.pack(padx=OTHER_PADX, pady=OTHER_PADY)

    update_listbox()

    created_root.mainloop()


########################################################################
########################################################################

#size calculation
###########################################

# Define the font size for the GUI
FONT_SIZE = int(screen_width * 0.01)

# Define the padding between elements
PAD = int(screen_width * 0.01)

# Define the size of the title label
TITLE_FONT_SIZE = int(screen_width * 0.015)
TITLE_PADX = int(screen_width * 0.013)
TITLE_PADY = int(screen_height * 0.023)

# Define the size of the radio buttons
RADIO_FONT_SIZE = int(screen_width * 0.011)
RADIO_PADX = int(screen_width * 0.013)
RADIO_PADY = int(screen_height * 0.019)
RADIO_IPADY = int(screen_height * 0.0045)

# Define the size of the choice label
CHOICE_FONT_SIZE = int(screen_width * 0.013)
CHOICE_PADX = int(screen_width * 0.013)
CHOICE_PADY = int(screen_height * 0.019)

# Define the size of the input entry
ENTRY_FONT_SIZE = int(screen_width * 0.014)
ENTRY_WIDTH = int(screen_width * 0.015)
ENTRY_PADX = int(screen_width * 0.013)
ENTRY_PADY = int(screen_height * 0.019)

# Define the size of the buttons
BUTTON_FONT_SIZE = int(screen_width * 0.015)
BUTTON_WIDTH = int(screen_width * 0.016)
BUTTON_PADX = int(screen_width * 0.013)
BUTTON_PADY = int(screen_height * 0.019)

# Define the size of the QR code label
QR_FONT_SIZE = int(screen_width * 0.016)
QR_PADX = int(screen_width * 0.013)
QR_PADY = int(screen_height * 0.019)

# Define the size of the scale slider
SLIDER_FONT_SIZE = int(screen_width * 0.014)
SLIDER_PADX = int(screen_width * 0.013)
SLIDER_PADY = int(screen_height * 0.019)
SLIDER_LENGTH = int(screen_height * 0.32)

LISTBOX_WIDTH = int(screen_width * 0.1)
LISTBOX_HEIGHT = int(screen_height * 0.1)
LISTBOX_FONT_SIZE = int(screen_width * 0.5)

OTHER_PADX = int(screen_width * 0.13)
OTHER_PADY = int(screen_height * 0.19)

CREATED_BUTTON_WIDTH = int(screen_width * 0.010)
CREATED_BUTTON_FONT_SIZE = int(screen_width * 0.012)

CREATED_FRAME_FONT_SIZE = int(screen_width * 0.13)
CREATED_PATH_FONT_SIZE = int(screen_width * 0.1)

######################################

#gui section

#green (background) #98FF98
#blue (buttons and listboxes) #00FFFF
#yeallow (different things) #FFFF9F
#pink bg's #fcc6d4

GREEN_COLOR = "#98FF98"
BLUE_COLOR = "#00FFFF"
PINK_COLOR = "#fcc6d4"

FONT = "Arial"
FONT = "Times"

title = Label(master=root, text=f"ARC QR Code Generator {VERSION}", bg=GREEN_COLOR, font=(FONT, TITLE_FONT_SIZE))
title.grid(row=0, column=1, padx=TITLE_PADX, pady=TITLE_PADY)

radio_frame = LabelFrame(master=root, text="Choose Type", bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE))
radio_frame.grid(row=1, column=0, padx=RADIO_PADX, pady=TITLE_PADY)

radio_var = StringVar()
radio_var.set("text")
radio_1 = Radiobutton(master=radio_frame, text="Text", variable=radio_var, value="text", activebackground=GREEN_COLOR, bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE), command=update_label)
radio_1.grid(row=0, column=0, padx=RADIO_PADX, pady=RADIO_PADY, ipady=RADIO_IPADY)
radio_2 = Radiobutton(master=radio_frame, text="URL", variable=radio_var, value="url", activebackground=GREEN_COLOR, bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE), command=update_label)
radio_2.grid(row=1, column=0, padx=RADIO_PADX, pady=RADIO_PADY, ipady=RADIO_IPADY)
radio_3 = Radiobutton(master=radio_frame, text="Email", variable=radio_var, value="email", activebackground=GREEN_COLOR, bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE), command=update_label)
radio_3.grid(row=2, column=0, padx=RADIO_PADX, pady=RADIO_PADY, ipady=RADIO_IPADY)
radio_4 = Radiobutton(master=radio_frame, text="Phone", variable=radio_var, value="phone", activebackground=GREEN_COLOR, bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE), command=update_label)
radio_4.grid(row=3, column=0, padx=RADIO_PADX, pady=RADIO_PADY, ipady=RADIO_IPADY)
radio_5 = Radiobutton(master=radio_frame, text="Contact", variable=radio_var, value="contact", activebackground=GREEN_COLOR, bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE), command=update_label)
radio_5.grid(row=4, column=0, padx=RADIO_PADX, pady=RADIO_PADY, ipady=RADIO_IPADY)
radio_6 = Radiobutton(master=radio_frame, text="Wifi", variable=radio_var, value="wifi", activebackground=GREEN_COLOR, bg=GREEN_COLOR, font=(FONT, RADIO_FONT_SIZE), command=update_label)
radio_6.grid(row=5, column=0, padx=RADIO_PADX, pady=RADIO_PADY, ipady=RADIO_IPADY)

main_frame = LabelFrame(master=root, text="Controls", bg=GREEN_COLOR, font=(FONT, FONT_SIZE))
main_frame.grid(row=1, column=1, padx=TITLE_PADX, pady=TITLE_PADY)

input_frame = LabelFrame(master=main_frame, text="Input", bg=GREEN_COLOR, font=(FONT, FONT_SIZE))
input_frame.pack(padx=TITLE_PADX, pady=TITLE_PADY)

choice_label = Label(master=input_frame, text=(radio_var.get()).title(), bg=GREEN_COLOR, font=(FONT, CHOICE_FONT_SIZE))
choice_label.grid(row=0, column=0, padx=CHOICE_PADX, pady=CHOICE_PADY)

qr_entry = ttk.Entry(master=input_frame, font=(FONT, ENTRY_FONT_SIZE), width=ENTRY_WIDTH)
qr_entry.grid(row=0, column=1, padx=20, pady=20)

create_btn = Button(master=main_frame, text="Create QR Code", bg=BLUE_COLOR, font=(FONT, BUTTON_FONT_SIZE), width=BUTTON_WIDTH, command=create)
create_btn.pack(padx=BUTTON_PADX, pady=BUTTON_PADY)

clear_btn = Button(master=main_frame, text="Clear", bg=BLUE_COLOR,  font=(FONT, BUTTON_FONT_SIZE), width=BUTTON_WIDTH, command=clear)
clear_btn.pack(padx=SLIDER_PADX, pady=SLIDER_PADY)

created_btn = Button(master=main_frame, text="Created QR Codes", bg=BLUE_COLOR,  font=(FONT, BUTTON_FONT_SIZE), width=BUTTON_WIDTH, command=show_all)
created_btn.pack(padx=SLIDER_PADX, pady=SLIDER_PADY)

qr_frame = LabelFrame(master=root, text="QR Code", bg=GREEN_COLOR, font=(FONT,QR_FONT_SIZE))
qr_frame.grid(row=1, column=3, padx=QR_PADX, pady=QR_PADY)

qr_label = Label(master=qr_frame, bg=GREEN_COLOR, text="")
qr_label.pack(padx=QR_PADX, pady=QR_PADY)

slider_frame = LabelFrame(master=root, text="Scale", bg=GREEN_COLOR, font=(FONT, SLIDER_FONT_SIZE))
slider_frame.grid(row=1, column=2, padx=20, pady=20)

style = ttk.Style()
style.theme_use('default')
style.configure("TScale", background=GREEN_COLOR, troughcolor=BLUE_COLOR)

scale_slider = ttk.Scale(master=slider_frame, from_=10, to=1, style="TScale", orient=VERTICAL, command=set_slider_label, length=SLIDER_LENGTH)
scale_slider.pack(padx=SLIDER_PADX, pady=SLIDER_PADY)
scale_slider.set(5)

slider_label = Label(master=slider_frame, text=int(scale_slider.get()), bg=GREEN_COLOR, font=(FONT, SLIDER_FONT_SIZE))
slider_label.pack(padx=SLIDER_PADX, pady=SLIDER_PADY)

update_thread = threading.Thread(target=check_for_update, daemon=True)
update_thread.start()

root.mainloop()
