def signature(signature):
    print("Eap used. By ", signature)

def publicsignature(signature):
    import tkinter as tk
    from tkinter import messagebox

    messagebox.showinfo("EAP Signature", signature)

def button(wind, name, text, pady, function):
    import tkinter as tk

    name = tk.Button(wind, text=text, command=function)
    name.pack(pady=pady)

def label(wind, name, text, pady):
    import tkinter as tk

    name = tk.Label(wind, text=text)
    name.pack(pady=pady)

def textbox(wind, name, pady):
    import tkinter as tk

    name = tk.Entry(wind)
    name.pack(pady=pady)

def windtmf(name, tmf):
    import tkinter as tk

    name.geometry(tmf)
    
def crash(name):
    import ctypes
    name.destroy()
    ctypes.CDLL(r"C:\Users\cliente\Desktop\Easy App Creator\app\AppTemplate\EAPCrashHandler.dll")
