from tkinter import *
from tkinter import ttk
import global_vars as bf
import main



#Multiscope variables
search_type = None
bourbon = None

############# Initialize GUI


window = Tk()
window.title("Bourbon Finder")
window.geometry('400x150')
window.configure(bg='#2b2b2b')
frame = Frame(window)
frame.configure(bg='#2b2b2b', pady=10)
frame.pack()


# Radio button selection for search type
textbox = LabelFrame(frame, text="What bourbon are you looking for?")
textbox.configure(bg='#2b2b2b', fg='#a9b7c6', pady=10)
textbox.pack(side=LEFT)
user_input = Entry(textbox, width=15)
user_input.configure(bg='#3a3f3f', fg='#cc7832')
user_input.pack()


# Radio button selection for search type
radio_buttons = LabelFrame(frame, text="Search Type")
radio_buttons.configure(bg='#2b2b2b', fg='#a9b7c6')
radio_buttons.pack(side=RIGHT)
search_value = IntVar()

radio_one = Radiobutton(radio_buttons, text='Single Search', value=0, variable=search_value)
radio_one.configure(bg='#2b2b2b', fg='#a9b7c6', activebackground='#cc7832')
radio_one.pack(anchor=W)

radio_two = Radiobutton(radio_buttons, text='Continuous', value=1, variable=search_value)
radio_two.configure(bg='#2b2b2b', fg='#a9b7c6', activebackground='#cc7832')
radio_two.pack(anchor=W)

"""reminder = Label(window, text="Note: it's better to search for a partial\n match "
                              "For example: Blanton is better than\n Blanton's")
reminder.configure(bg='#2b2b2b', fg='#a9b7c6')"""


###### Button configuration

def on_click():

    search = search_value.get()
    bf.bourbon = user_input.get()
    main.run()
    #print('test')

"""
def on_stop():
   global running
   running = False"""

bottom_frame = Frame(frame)
bottom_frame.pack(side=BOTTOM)
button = Button(window, text="Search", command=on_click)
button.configure(bg='#3a3f3f', fg='#a9b7c6', activebackground='#cc7832')
button.pack(side=BOTTOM)

#stop = ttk.Button(window, text="Stop", command=on_stop)






window.mainloop()