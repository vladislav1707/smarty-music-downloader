import tkinter as tk

win = tk.Tk()     # EN: main window. RU: главное окно
win.title("getMusic3 GUI")     # EN: window title. RU: заголовок окна
win.geometry("300x300")    # EN: window size. RU: размеры окна

status = tk.Label(text="WORK IN PROGRESS") # EN: status label. RU: метка статуса
status.pack()    # place the label in the window. RU: разместить метку в окне

win.mainloop()
